"""Stage only the verified x64 Vulkan loader; no SDK, driver or installer runs."""

import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSET = 'VulkanRT-X64-1.4.363.0-Components.zip'
URL = 'https://sdk.lunarg.com/sdk/download/1.4.363.0/windows/' + ASSET + '?Human=true'
SHA256 = 'a25a927aa8b9f0371048f1861cf88ac3b9bc9b1fb332c42d897c8ab32695769a'


def fetch_vulkan():
    archive = ROOT / 'downloads' / ASSET
    archive.parent.mkdir(exist_ok=True)
    if not archive.is_file():
        request = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=120) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != SHA256:
        raise RuntimeError('Vulkan runtime archive checksum mismatch')
    prefix = ASSET.removesuffix('.zip') + '/'
    with zipfile.ZipFile(archive) as bundle:
        payload = bundle.read(prefix + 'x64/vulkan-1.dll')
        license_text = bundle.read(prefix + 'VulkanRT-License.txt')
    target = ROOT / 'bin'
    target.mkdir(exist_ok=True)
    (target / 'vulkan-1.dll').write_bytes(payload)
    notices = ROOT / 'licenses/vulkan'
    notices.mkdir(parents=True, exist_ok=True)
    (notices / 'VulkanRT-License.txt').write_bytes(license_text)
    (notices / 'SOURCE.json').write_text(json.dumps({
        'version': '1.4.363.0', 'url': URL, 'archive_sha256': SHA256,
        'file': 'bin/vulkan-1.dll', 'dll_sha256': hashlib.sha256(payload).hexdigest(),
        'source': 'https://github.com/KhronosGroup/Vulkan-Loader/tree/vulkan-sdk-1.4.363.0',
        'purpose': 'Required MPV import dependency; rendering remains D3D11.'
    }, indent=2) + '\n', encoding='utf-8')
    print('Verified x64 Vulkan loader staged (' + str(len(payload)) + ' bytes)')


if __name__ == '__main__':
    fetch_vulkan()
