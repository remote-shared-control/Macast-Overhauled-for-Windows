"""Offline resource and real named-pipe startup check used by release builds."""

import hashlib
import json
import logging
import time

import cherrypy

from .resources import resource_root, mpv_path
from .utils import Setting


def diagnose():
    root = resource_root()
    report = {'ok': False, 'resource_root': str(root), 'mpv': mpv_path()}
    required = ['bin/mpv.exe', 'macast/.version', 'macast/xml/Description.xml',
                'macast/assets/icon.ico', 'macast/assets/fonts/element-icons.woff',
                'mpv_ui/scripts/modernz/main.lua', 'mpv_ui/modernz.conf',
                'mpv_ui/fonts/modernz-icons.ttf', 'bundled_plugins/manifest.json']
    report['missing'] = [name for name in required if not (root / name).is_file()]
    if report['missing']:
        return report
    manifest = json.loads((root / 'bundled_plugins/manifest.json').read_text(encoding='utf-8'))
    report['plugins'] = [p['title'] for p in manifest['plugins']]
    report['checksums_ok'] = all(hashlib.sha256((root / 'bundled_plugins' / p['path']).read_bytes()).hexdigest()
                                 == p['sha256'] for p in manifest['plugins'])
    from macast_renderer.mpv import MPVRenderer
    from .protocol import Protocol
    # Do not bind a network port or install/update user plugins for this check.
    protocol = Protocol()
    get_protocol = lambda: protocol
    cherrypy.engine.subscribe('get_protocol', get_protocol)
    renderer = MPVRenderer(path=mpv_path())
    report['application_version'] = Setting.get_version()
    errors = []

    class Capture(logging.Handler):
        def emit(self, record):
            errors.append(record.getMessage())

    capture = Capture(level=logging.WARNING)
    logger = logging.getLogger('MPVRenderer')
    logger.addHandler(capture)
    before = time.monotonic()
    client = None
    try:
        renderer.start()
        deadline = before + 15
        while time.monotonic() < deadline and not renderer.ipc_once_connected:
            time.sleep(0.02)
        report['ipc_connected'] = renderer.ipc_once_connected
        report['startup_ms'] = round((time.monotonic() - before) * 1000)
        report['mpv_version'] = '.'.join(map(str, renderer.mpv_version))
        if renderer.ipc_once_connected:
            from macast_renderer.ipc import WindowsQueryClient
            client = WindowsQueryClient(renderer.mpv_sock)
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline:
                try:
                    report['danmaku_state'] = client.command(['get_property', 'user-data/macast/danmaku'])
                    break
                except RuntimeError:
                    time.sleep(0.02)
            report['scripts'] = client.command(['get_property', 'options/scripts'])
            report['modernz_loaded'] = any('modernz' in str(script).lower() for script in report['scripts'])
            report['hardware_decode'] = client.command(['get_property', 'hwdec'])
            report['secondary_sub_position'] = client.command(['get_property', 'secondary-sub-pos'])
            client.command(['script-message-to', 'modernz', 'macast-ui-scale', '1.25'])
            client.command(['set_property', 'user-data/macast/danmaku/enabled', False])
            report['danmaku_toggle_ok'] = client.command(['get_property', 'user-data/macast/danmaku/enabled']) is False
    except Exception as error:
        report['error'] = str(error)
    finally:
        if client is not None:
            client.close()
        renderer.stop()
        logger.removeHandler(capture)
        cherrypy.engine.unsubscribe('get_protocol', get_protocol)
    report['player_warnings'] = errors
    report['player_exit_code'] = renderer.proc.returncode if renderer.proc is not None else None
    report['threads_stopped'] = not any(t and t.is_alive() for t in (renderer.mpv_thread, renderer.ipc_thread))
    report['ok'] = bool(report.get('ipc_connected') and report.get('modernz_loaded')
                        and report.get('danmaku_toggle_ok') and report['checksums_ok'] and report['threads_stopped']
                        and report.get('secondary_sub_position') == 100
                        and report['application_version'] == (root / 'macast/.version').read_text().strip()
                        and not report.get('error') and not errors)
    return report
