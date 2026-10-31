"""Short-lived query client for offline Windows player diagnostics."""

import json
import time


class WindowsQueryClient:
    def __init__(self, name):
        import _winapi
        from multiprocessing.connection import PipeConnection
        handle = _winapi.CreateFile(name, _winapi.GENERIC_READ | _winapi.GENERIC_WRITE,
                                   0, _winapi.NULL, _winapi.OPEN_EXISTING,
                                   _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL)
        self.pipe = PipeConnection(handle)
        self.request_id = 0
        self.buffer = b''

    def command(self, command, timeout=3):
        self.request_id += 1
        payload = {'command': command, 'request_id': self.request_id}
        self.pipe.send_bytes((json.dumps(payload) + '\n').encode('utf-8'))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                reply = json.loads(line)
                if reply.get('request_id') == self.request_id:
                    if reply.get('error') != 'success':
                        raise RuntimeError(str(reply))
                    return reply.get('data')
            if self.pipe.poll(min(0.1, max(0, deadline - time.monotonic()))):
                self.buffer += self.pipe.recv_bytes(1024 * 1024)
        raise TimeoutError('MPV query timed out: ' + command[0])

    def close(self):
        self.pipe.close()
