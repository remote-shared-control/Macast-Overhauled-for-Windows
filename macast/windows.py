"""Small Windows integrations; no framework, service or resident helper."""

import ctypes
from ctypes import wintypes
import hashlib
import ipaddress
import os


class SingleInstance:
    def __init__(self, config_directory):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        kernel.CreateMutexW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel = kernel
        identity = hashlib.sha256(os.path.normcase(os.path.abspath(config_directory)).encode()).hexdigest()[:24]
        self.handle = kernel.CreateMutexW(None, False, 'Local\\MacastOverhauled-' + identity)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        self.already_running = ctypes.get_last_error() == 183

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def interface_addresses(blocked=(), additional=()):
    """Enumerate active IPv4 adapters, including Ethernet without a default route."""
    import psutil
    import socket
    blocked, additional = set(blocked), set(additional)
    stats = psutil.net_if_stats()
    result = set()
    for name, addresses in psutil.net_if_addrs().items():
        if name in blocked:
            continue
        if name not in additional and (name not in stats or not stats[name].isup):
            continue
        for address in addresses:
            if address.family != socket.AF_INET or not address.netmask:
                continue
            ip = ipaddress.ip_address(address.address)
            if ip.is_loopback or ip.is_link_local or ip.is_unspecified:
                continue
            result.add((address.address, address.netmask))
    return result
