# Third-party notices — Windows build

Macast-Overhauled for Windows derives from xfangfang/Macast (GPL-3.0) and the local Macast-Overhauled macOS fork. Original copyright statements remain in the source. Base revisions are recorded in SOURCE-REVISIONS.json.

| Component | Purpose | License/source record |
| --- | --- | --- |
| Macast | Tray receiver, DLNA, server and renderer framework | LICENSE, GPL-3.0 |
| Macast-plugins / xfangfang and contributors | NVA protocol implementation | Macast-plugins/LICENSE, MIT |
| ModernZ / Samillion and prior OSC contributors | Modified blue controls, DPI sizing and danmaku | mpv_ui/LICENSE.ModernZ, LGPL-2.1; mpv_ui/UPSTREAM.json and original README |
| Fluent System Icons / Microsoft | UI font icons | licenses/icons/Fluent-System-Icons-MIT.txt |
| Material Symbols / Google | UI font icons | licenses/icons/Material-Symbols-Apache-2.0.txt |
| Vue, Vue Resource, Element UI | Local settings page | licenses/frontend/ |
| CPython | Frozen interpreter | Documentation/licenses/LICENSE.Python.txt |
| CherryPy, cheroot, Requests, lxml, Pillow, pystray, pyperclip, psutil, appdirs and transitive Python dependencies | Runtime support | Documentation/licenses/python/ and PYTHON-PACKAGES.json |
| MPV, FFmpeg, libplacebo and native dependencies | Playback | Documentation/licenses/mpv/ and MPV-SOURCE.json |
| PyInstaller | Packaging bootloader | GPL with distribution exception; upstream project documentation |

The player is the unmodified shinchiro baseline x64 build `20261021`, MPV commit `e471496c56`, FFmpeg commit `9a861e968`. The downloaded archive SHA256 is `4a355f3e89c83fabc730d33fb4e759dfec747806ed2287b61a90d1681b83e8d3`. Source and build-recipe links are recorded under licenses/mpv/SOURCES.md. Windows 10/11 system D3DCompiler_47 is used; the upstream archive's _43 DLL, installer and updater are excluded.

The application source ZIP supplies the local Python/Lua/config/build changes, including the modified ModernZ and NVA sources. Native player components are independently built upstream; this application snapshot is not their complete corresponding source. Any public binary redistributor must also make the complete corresponding sources/build material for those native GPL/LGPL components available under their respective terms. Component licenses and original credits remain applicable.

No PotPlayer, IINA, Cocoa, PyObjC, netifaces or pywin32 code is included in the Windows runtime. Their historical references in the workspace do not describe packaged dependencies.
