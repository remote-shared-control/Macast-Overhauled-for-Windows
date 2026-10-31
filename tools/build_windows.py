"""Build and verify the portable Windows x64 folder and ZIP from a clean venv."""

import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile

from prepare_plugins import prepare_plugins

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True, **kwargs)


def runtime_packages():
    from packaging.requirements import Requirement
    pending = ['appdirs', 'cherrypy', 'lxml', 'pillow', 'requests', 'psutil', 'pystray', 'pyperclip']
    found = {}
    while pending:
        name = pending.pop()
        distribution = metadata.distribution(name)
        canonical = distribution.metadata['Name'].lower().replace('_', '-')
        if canonical in found:
            continue
        found[canonical] = distribution
        for raw in distribution.requires or []:
            req = Requirement(raw)
            if req.marker is None or req.marker.evaluate({'extra': ''}):
                pending.append(req.name)
    return found


def documentation(output, mpv):
    docs = output / 'Documentation'
    docs.mkdir(exist_ok=True)
    for name in ['README_ZH.md', 'README.md', 'BUILDING.md', 'RELEASE_NOTES.md',
                 'THIRD_PARTY_NOTICES.md', 'LICENSE', 'SOURCE-REVISIONS.json', 'VALIDATION.md']:
        shutil.copy2(ROOT / name, docs / name)
    for section in ('frontend', 'icons', 'mpv'):
        if (ROOT / 'licenses' / section).is_dir():
            shutil.copytree(ROOT / 'licenses' / section, docs / 'licenses' / section, dirs_exist_ok=True)
    shutil.copy2(ROOT / 'mpv_ui/LICENSE.ModernZ', docs / 'licenses/LICENSE.ModernZ')
    shutil.copy2(ROOT / 'mpv_ui/UPSTREAM.json', docs / 'licenses/ModernZ-UPSTREAM.json')
    shutil.copy2(ROOT / 'Macast-plugins/LICENSE', docs / 'licenses/LICENSE.Macast-plugins')
    if (mpv / 'MPV-SOURCE.json').is_file():
        shutil.copy2(mpv / 'MPV-SOURCE.json', docs / 'licenses/MPV-SOURCE.json')
    for name in ('modernz-windows.png', 'report.json'):
        capture = ROOT / 'build/player-check' / name
        if capture.is_file():
            target = docs / 'Player-check' / name
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(capture, target)
    inventory = []
    for name, distribution in sorted(runtime_packages().items()):
        license_dir = docs / 'licenses/python' / name
        license_dir.mkdir(parents=True, exist_ok=True)
        raw_metadata = distribution.read_text('METADATA') or distribution.read_text('PKG-INFO') or ''
        (license_dir / 'METADATA.txt').write_text(raw_metadata, encoding='utf-8')
        for file in distribution.files or []:
            if file.parts[0].endswith('.dist-info') and any(
                    word in str(file).lower() for word in ['license', 'copying', 'notice']):
                source = Path(distribution.locate_file(file))
                if source.is_file():
                    relative = Path(*file.parts[1:])
                    target = license_dir / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
        inventory.append({'name': distribution.metadata['Name'], 'version': distribution.version})
    (docs / 'licenses/PYTHON-PACKAGES.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    python_license = Path(sys.base_prefix) / 'LICENSE.txt'
    if python_license.is_file():
        shutil.copy2(python_license, docs / 'licenses/LICENSE.Python.txt')


def source_archive(destination):
    omitted = {'.venv', '.git', 'build', 'dist', 'downloads', 'bin', '__pycache__',
               '.pytest_cache', '.idea', '.vscode'}
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(ROOT.rglob('*')):
            rel = path.relative_to(ROOT)
            # Keep macOS/upstream references in the working copy while keeping
            # this Windows source delivery focused and independent of them.
            legacy_dirs = {'licenses/native-supplement', 'Macast-plugins/potplayer',
                'Macast-plugins/iina', 'Macast-plugins/bolan-iina', 'Macast-plugins/pi-fm-rds',
                'Macast-plugins/web', 'Macast-plugins/live'}
            legacy_files = {'setup_py2app.py', 'Dockerfile', 'requirements/darwin.txt',
                'build-requirements.lock.txt', 'tools/build_macos.sh', 'tools/normalize_rpaths.py',
                'tools/prepare_distribution.py', 'docs/macOS-27-ZH.md',
                '.github/workflows/build-macast.yaml', '.github/workflows/release-macos.yml'}
            if (any(part in omitted for part in rel.parts) or path.suffix in ('.pyc', '.log', '.zip')
                    or rel.as_posix() in legacy_files
                    or any(rel.as_posix().startswith(directory + '/') for directory in legacy_dirs)):
                continue
            if path.is_file():
                archive.write(path, 'Macast-Overhauled-Windows/' + rel.as_posix())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mpv-dir', type=Path, default=ROOT / 'bin')
    args = parser.parse_args()
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64') or sys.version_info[:2] != (3, 12):
        raise SystemExit('Build with 64-bit CPython 3.12 on Windows 10/11.')
    mpv = args.mpv_dir.resolve()
    if not (mpv / 'mpv.exe').is_file():
        raise SystemExit('Run python tools/fetch_mpv.py first, or pass --mpv-dir.')
    entries = prepare_plugins(ROOT / 'Macast-plugins', ROOT / 'bundled_plugins', 'win32', {'nirvana'})
    if len(entries) != 1:
        raise RuntimeError('Expected only the NVA protocol plugin')
    run(sys.executable, '-m', 'pytest', 'tests', 'Macast-plugins/tests', '-q')
    env = dict(os.environ, MACAST_MPV_DIR=str(mpv), PYTHONUTF8='1')
    run(sys.executable, '-m', 'PyInstaller', '--noconfirm', 'Macast-Windows.spec', env=env)
    output = ROOT / 'dist/Macast-Overhauled-Windows'
    report = ROOT / 'build/frozen-diagnostic.json'
    run(output / 'Macast.exe', '--config-dir', ROOT / 'build/frozen-check-config', '--diagnose', report, timeout=30)
    if not json.loads(report.read_text(encoding='utf-8'))['ok']:
        raise RuntimeError('Frozen player diagnostics failed')
    smoke_report = ROOT / 'build/frozen-smoke.json'
    run(output / 'Macast.exe', '--config-dir', ROOT / 'build/frozen-smoke-config', '--smoke-test', smoke_report, timeout=35)
    documentation(output, mpv)
    version = (ROOT / 'macast/.version').read_text().strip()
    source_archive(output / 'Documentation' / ('Macast-Windows-Source-v' + version + '.zip'))
    shutil.copy2(report, output / 'Documentation/BUILD-DIAGNOSTIC.json')
    shutil.copy2(smoke_report, output / 'Documentation/BUILD-SMOKE.json')
    archive = ROOT / 'dist' / ('Macast-Overhauled-Windows-v' + version + '-x64.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for file in sorted(output.rglob('*')):
            if file.is_file():
                bundle.write(file, file.relative_to(output.parent).as_posix())
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    print(str(archive) + '\nSHA256: ' + digest)


if __name__ == '__main__':
    main()
