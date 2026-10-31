"""Fetch the fixed baseline x64 build. Never substitute x86-64-v3/v4 binaries."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request
from fetch_vulkan import fetch_vulkan

ROOT = Path(__file__).resolve().parents[1]
ASSET = 'mpv-x86_64-20261021-git-e471496c56.7z'
URL = 'https://github.com/shinchiro/mpv-winbuild-cmake/releases/download/20261021/' + ASSET
SHA256 = '4a355f3e89c83fabc730d33fb4e759dfec747806ed2287b61a90d1681b83e8d3'


def fetch():
    archive = ROOT / 'downloads' / ASSET
    archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        print('Downloading ' + ASSET, flush=True)
        with urllib.request.urlopen(URL, timeout=120) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != SHA256:
        raise RuntimeError('MPV checksum mismatch. Remove the downloaded archive and retry.')
    target = ROOT / 'bin'
    target.mkdir(exist_ok=True)
    # Older Windows/Server bsdtar builds lack the LZMA codec. GitHub's
    # Windows runners provide 7-Zip; recent Windows 11 tar also works.
    seven_zip = shutil.which('7z') or shutil.which('7zz')
    if not seven_zip:
        candidate = Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / '7-Zip/7z.exe'
        if candidate.is_file():
            seven_zip = str(candidate)
    if seven_zip:
        subprocess.run([seven_zip, 'x', '-y', '-o' + str(target), str(archive)], check=True)
    else:
        try:
            subprocess.run(['tar', '-xf', str(archive), '-C', str(target)], check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            raise RuntimeError('This tar build cannot extract the MPV archive. Install 7-Zip and retry.') from error
    (target / 'MPV-SOURCE.json').write_text(json.dumps({
        'asset': ASSET, 'url': URL, 'sha256': SHA256, 'release': '20261021',
        'mpv_commit': 'e471496c56', 'ffmpeg_commit': '9a861e968',
        'source': 'https://github.com/shinchiro/mpv-winbuild-cmake',
    }, indent=2) + '\n', encoding='utf-8')
    print('Verified and extracted ' + ASSET)
    fetch_vulkan()


if __name__ == '__main__':
    fetch()
