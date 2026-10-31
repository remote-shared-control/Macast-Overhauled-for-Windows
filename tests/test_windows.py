import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest

from macast import bundled_plugins, resources
from macast.utils import Setting
from macast.windows import interface_addresses, SingleInstance
from macast_renderer.ui import player_ui_options
from tools.prepare_plugins import prepare_plugins


ROOT = Path(__file__).resolve().parents[1]


def test_windows_tray_icon_is_decodable():
    from PIL import Image
    with Image.open(ROOT / 'macast/assets/icon.ico') as icon:
        icon.load()
        assert icon.size == (256, 256)


def test_frozen_resources_use_pyinstaller_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    monkeypatch.setenv('RESOURCEPATH', 'unused-macos-path')
    assert bundled_plugins.bundle_directory() == tmp_path / 'bundled_plugins'


def test_frozen_settings_resources_use_macast_package(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    monkeypatch.setattr(Setting, 'base_path', None)
    assert Path(Setting.get_base_path('.version')) == tmp_path / 'macast/.version'


def test_source_resources_ignore_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert resources.resource_root() == ROOT
    options = player_ui_options(1.5)
    assert '--osc=no' in options
    assert '--script=' + str(ROOT / 'mpv_ui/scripts/modernz') in options
    assert '--script-opts-append=modernz-macast_ui_scale=1.5' in options


def test_windows_adapter_filtering(monkeypatch):
    import psutil
    addr = lambda ip, mask='255.255.255.0': SimpleNamespace(family=socket.AF_INET, address=ip, netmask=mask)
    monkeypatch.setattr(psutil, 'net_if_stats', lambda: {
        name: SimpleNamespace(isup=name != 'Down') for name in ['Ethernet', 'Wi-Fi', 'Loopback', 'APIPA', 'Down']})
    monkeypatch.setattr(psutil, 'net_if_addrs', lambda: {
        'Ethernet': [addr('192.168.1.20')], 'Wi-Fi': [addr('192.168.2.20')],
        'Loopback': [addr('127.0.0.1')], 'APIPA': [addr('169.254.2.3')], 'Down': [addr('10.0.0.1')]})
    assert interface_addresses(blocked=['Wi-Fi']) == {('192.168.1.20', '255.255.255.0')}
    assert ('10.0.0.1', '255.255.255.0') in interface_addresses(additional=['Down'])


def test_single_instance_closes_cleanly(tmp_path):
    first = SingleInstance(str(tmp_path))
    second = SingleInstance(str(tmp_path))
    try:
        assert not first.already_running
        assert second.already_running
    finally:
        first.close()
        second.close()
    third = SingleInstance(str(tmp_path))
    try:
        assert not third.already_running
    finally:
        third.close()


def write_manifest(source, content):
    target = source / 'protocol/nirvana.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    manifest = {'schema': 1, 'plugins': [{'path': 'protocol/nirvana.py', 'version': '0.40',
                                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}]}
    (source / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')


def test_bundled_plugin_updates_keep_custom_edits(monkeypatch, tmp_path):
    source, config = tmp_path / 'bundle', tmp_path / 'config'
    monkeypatch.setattr(bundled_plugins, 'bundle_directory', lambda: source)
    write_manifest(source, 'original = 1\n')
    bundled_plugins.install_bundled_plugins(config)
    target = config / 'protocol/nirvana.py'
    target.write_text('custom = 2\n', encoding='utf-8')
    write_manifest(source, 'updated = 3\n')
    bundled_plugins.install_bundled_plugins(config)
    assert target.read_text() == 'custom = 2\n'


def test_bundled_plugin_managed_update_keeps_backup(monkeypatch, tmp_path):
    source, config = tmp_path / 'bundle', tmp_path / 'config'
    monkeypatch.setattr(bundled_plugins, 'bundle_directory', lambda: source)
    write_manifest(source, 'original = 1\n')
    bundled_plugins.install_bundled_plugins(config)
    write_manifest(source, 'updated = 3\n')
    bundled_plugins.install_bundled_plugins(config)
    assert (config / 'protocol/nirvana.py').read_text() == 'updated = 3\n'
    backups = list((config / 'bundled-plugin-backups').glob('*/protocol/nirvana.py'))
    assert len(backups) == 1 and backups[0].read_text() == 'original = 1\n'


def test_windows_bundle_contains_only_nva(tmp_path):
    entries = prepare_plugins(ROOT / 'Macast-plugins', tmp_path, 'win32', {'nirvana'})
    assert [entry['title'] for entry in entries] == ['NVA Protocol']
    assert not (tmp_path / 'renderer').exists()


@pytest.mark.skipif(not (ROOT / 'bin/mpv.exe').is_file(), reason='Pinned MPV not downloaded')
def test_real_player_from_unicode_path(tmp_path):
    working = tmp_path / '中文 空格'
    working.mkdir()
    report = working / 'report.json'
    result = subprocess.run([sys.executable, str(ROOT / 'Macast.py'), '--config-dir', str(working / 'config'),
                             '--diagnose', str(report)], cwd=working, timeout=25)
    data = json.loads(report.read_text(encoding='utf-8'))
    assert result.returncode == 0, data
    assert data['ok'], data
    assert data['application_version'] == (ROOT / 'macast/.version').read_text().strip()
    assert data['modernz_loaded'] and data['danmaku_toggle_ok'] and data['threads_stopped']


@pytest.mark.skipif(not (ROOT / 'bin/mpv.exe').is_file(), reason='Pinned MPV not downloaded')
def test_first_launch_tray_http_and_nva_shutdown(tmp_path):
    report = tmp_path / 'receiver.json'
    result = subprocess.run([sys.executable, str(ROOT / 'Macast.py'), '--config-dir', str(tmp_path / 'fresh-config'),
                             '--smoke-test', str(report)], cwd=ROOT, timeout=30)
    data = json.loads(report.read_text(encoding='utf-8'))
    assert result.returncode == 0, data
    assert data['ok'], data
    assert data['nva_handshake'] and data['shutdown_clean']
