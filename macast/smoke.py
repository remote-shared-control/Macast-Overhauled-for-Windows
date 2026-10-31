"""Release smoke check of the actual tray, bundled plugin, HTTP and NVA server."""

import http.client
import socket
import threading
import time
import traceback

import cherrypy

from .macast import Macast
from .protocol import DLNAProtocol
from .resources import mpv_path
from .utils import Setting
from macast_renderer.mpv import MPVRenderer


def run_smoke():
    report = {'ok': False}
    start = time.monotonic()
    app = Macast(MPVRenderer(path=mpv_path()), DLNAProtocol())

    def check():
        connection = None
        try:
            deadline = time.monotonic() + 15
            renderer = app.service.renderer
            while time.monotonic() < deadline:
                if (cherrypy.engine.state == cherrypy.engine.states.STARTED
                        and renderer.ipc_once_connected and app.app.visible):
                    break
                time.sleep(0.02)
            report['startup_ms'] = round((time.monotonic() - start) * 1000)
            report['protocol'] = type(app.service.protocol).__name__
            report['renderer'] = type(renderer).__name__
            report['ipc'] = renderer.ipc_once_connected
            report['tray_running'] = app.app.visible
            import psutil
            report['receiver_rss_mib'] = round(psutil.Process().memory_info().rss / (1024 * 1024), 1)
            report['player_rss_mib'] = round(psutil.Process(renderer.proc.pid).memory_info().rss / (1024 * 1024), 1)
            port = cherrypy.server.bound_addr[1]
            statuses = {}
            for path in ['/description.xml', '/?page=1', '/assets/vue@2.6.14.js',
                         '/assets/fonts/element-icons.woff', '/dlna/AVTransport.xml']:
                request = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
                request.request('GET', path)
                response = request.getresponse()
                payload = response.read()
                statuses[path] = response.status if payload else 0
                request.close()
            report['http'] = statuses
            connection = socket.create_connection(('127.0.0.1', port), timeout=3)
            connection.sendall(b'SETUP /projection NVA/1.0\r\nSession: smoke\r\nUUID: smoke-phone\r\nContent-Length: 0\r\n\r\n')
            response = b''
            while b'\r\n\r\n' not in response:
                data = connection.recv(4096)
                if not data:
                    break
                response += data
            report['nva_handshake'] = response.startswith(b'NVA/1.0 200')
            report['ok'] = bool(report['protocol'] == 'NVAProtocol' and report['ipc']
                                and report['tray_running'] and report['nva_handshake']
                                and all(code == 200 for code in statuses.values()))
        except Exception:
            report['error'] = traceback.format_exc()
        finally:
            if connection is not None:
                connection.close()
            app.quit(None)

    checker = threading.Thread(target=check, name='RELEASE_SMOKE', daemon=True)
    checker.start()
    app.start()
    checker.join(timeout=10)
    report['shutdown_clean'] = not app.service.thread.is_alive() and not app.service.renderer.mpv_thread.is_alive()
    report['ok'] = report['ok'] and report['shutdown_clean']
    return report
