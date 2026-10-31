# Macast-Overhauled · Plugin-integrated edition for Windows

[简体中文](README_ZH.md) | [Build guide](BUILDING.md) | [Open-source licenses](THIRD_PARTY_NOTICES.md)

Want to watch a video from your phone on your Windows PC? Macast sits in the system tray and receives videos, music, and pictures. Music and picture casting use standard DLNA only.

This edition builds on [xfangfang's Macast](https://github.com/xfangfang/Macast), porting the plugin and player changes from [Macast-Overhauled for macOS](https://github.com/frienkie/Macast-Overhauled) to Windows 10 and Windows 11. It brings Bilibili casting, a bundled MPV player, and [ModernZ](https://github.com/Samillion/ModernZ) controls together. Extract the portable package without hunting down a separate player or plugin files.

This derivative is maintained independently. The Windows program is still named **Macast.exe**.

## Features

- **Phone casting** through standard DLNA or Bilibili's NVA protocol.
- **Bundled player** with MPV and runtime dependencies; no separate player or Python installation is required.
- **Quality selection** from the casting client using available DASH video tracks and matching audio.
- **Independent danmaku controls** for comments and ordinary subtitles, synchronized with the phone's danmaku switch.
- **Automatic UI scaling** for monitor DPI, window size, and fullscreen mode, with additional size presets.
- **Lightweight ModernZ interface** with blue accents and no extra thumbnail processes, video filters, or image enhancement passes.
- **Automatic plugin installation** for the bundled NVA plugin. Customized copies stay in place when you install a newer build.

## Installation

### Requirements

- Windows 10 22H2 or Windows 11, Intel / AMD **x64 (64-bit)**.
- The current package uses a baseline x86-64 MPV build. No 32-bit or native ARM64 package is provided.
- Phone and PC on the same local network, with communication between devices allowed.

### Steps

1. Download [**Macast-Overhauled-Windows-v0.8.1-x64.zip**](https://github.com/remote-shared-control/Macast-Overhauled-for-Windows/releases/latest/download/Macast-Overhauled-Windows-v0.8.1-x64.zip) from Releases.
2. Extract the **entire folder** from the ZIP to a fixed location on your PC.
3. Open **Macast.exe**. Its icon appears in the system tray.
4. If Windows Firewall prompts, allow Macast to receive connections on your own private network.

Keep **_internal** beside **Macast.exe**; copying the EXE alone is insufficient. Paths containing Chinese characters or spaces are supported. The current portable build is not code-signed.

### Getting a newer build

This edition does not check for Macast updates online or show upstream version prompts. To upgrade, quit Macast, download a newer ZIP from this project, extract its complete folder, and start the new version. Bundled plugins that you have not changed update on the next launch; your own edits stay in place.

## Usage

### Bilibili casting

1. Right-click Macast's tray icon and confirm **NVA Protocol** and **MPV Renderer** in settings; these are the first-launch defaults.
2. Open a video in the phone's Bilibili client and tap its cast button.
3. Select **我的小电视** in the device list.
4. Control playback, seeking, and available quality levels from the phone or use the PC player's controls.

Available quality levels depend on the video, server response, and account permissions. The application cannot unlock unavailable resolutions.

### Standard DLNA casting

Select **DLNA Protocol** in Macast, then discover and select the receiver from a DLNA-compatible phone application. The advertised device name follows your Macast settings. NVA also extends DLNA; select plain DLNA if a client needs it for compatibility.

### Player controls

Settings and player controls use English. Media titles, subtitle text, and danmaku keep their original language. Move the pointer toward the bottom of the player to reveal its controls.

| Control | Function |
| --- | --- |
| Play / Pause | Control the current video |
| Timeline | Seek to a playback position |
| Volume | Adjust volume or mute |
| **Subtitles** icon | Select an ordinary subtitle track, or **Off** |
| **Danmaku** speech bubble | Toggle comments independently; shown when danmaku is available |
| Fullscreen | Enter or leave fullscreen |

Subtitles and danmaku have independent switches. Turning subtitles off leaves danmaku available, and the phone's danmaku switch stays synchronized. The subtitle button may be unavailable if the video provides no ordinary captions. Normal subtitles move above the visible controls while danmaku keeps its independent position.

### Large and high-DPI displays

Open **Player UI Size** in Macast settings:

| Option | Effect |
| --- | --- |
| **Automatic (DPI)** | Scale with monitor DPI, window size, and fullscreen mode |
| **Automatic + 25%** | Enlarge the automatic size by 25% |
| **Automatic + 50%** | Enlarge the automatic size by 50% |

Changes apply immediately without restarting the player.

## Plugins and bundled player

The NVA plugin installs into the current user's configuration directory on first launch. Upgrades update managed, unmodified copies and back up replaced files; customized versions are preserved.

| Component | Purpose |
| --- | --- |
| Nirvana / NVA Protocol | Bilibili casting; source in [Macast-plugins/nirvana](Macast-plugins/nirvana/) |
| DLNA Protocol | Built-in standard DLNA protocol |
| MPV Renderer | The sole bundled player, with ModernZ and independent subtitle/danmaku controls |

The Windows edition uses only the bundled MPV and does not include PotPlayer or other external player integrations. D3D11 output and automatic hardware decoding are enabled by default. Disable **Hardware Decode** in settings when troubleshooting GPU drivers.

## FAQ

### Phone cannot find the receiver?

Check that both devices share the same network and Windows Firewall allows incoming Macast connections on your private network. Guest networks, wireless client isolation, and some VPNs can prevent discovery. Bilibili casting also requires **NVA Protocol**.

### Selected a device, but no player opened?

Check that **MPV Renderer** is selected and the portable package's **_internal** folder has not been moved or removed. Select the video again and inspect `application.log` through **Open Config Directory**.

### Why is 1080P unavailable?

First check that the video and account have access to that quality on the phone. The server response determines available tracks. Network errors, expired media URLs, or client protocol changes can also affect playback.

### Why does switching videos take a moment?

The player clears the previous frame and loads the new video. Quality and URL requests, transfer, decoder preparation, and buffering still take time. For unusually long delays, inspect stage timings in `latency.log` in the configuration directory.

### Configuration and issue reports

Choose **Open Config Directory** to open:

```text
%LOCALAPPDATA%\Macast-Overhauled
```

The `protocol/` folder contains the NVA plugin; `bundled-plugin-backups/` contains upgrade backups. `application.log` and `latency.log` rotate. Optional current-user login startup is available in the tray settings and is disabled by default.

When reporting a problem, include the Windows version, CPU / GPU, selected protocol, phone client version, reproduction steps, and relevant logs. Remove account information, tokens, and complete media URLs before sharing logs. Identify this derivative edition so it can be distinguished from upstream.

## Good to know

- The current package targets Windows 10 22H2 / Windows 11 x64. It has passed 37 regression checks plus local rendering, NVA handshake, and portable-path checks on Windows 11. Windows 10 devices, actual phone casting, other GPUs, and mixed-DPI displays still require device validation.
- Multi-segment `durl` videos are not supported. DRM, special audio tracks, and some client protocol combinations may not play.
- Client or service API changes may affect casting. The media service controls account and content access.

## Build from source

See [BUILDING.md](BUILDING.md). Keep the included `Macast-plugins/` directory and build on Windows x64 with Python 3.12. The portable package includes bilingual documentation, license records, and a `Documentation/Macast-Windows-Source-v0.8.1.zip` snapshot of the modified application and plugins.

The folder-based build avoids per-launch extraction. Forward and backward media caches are capped at 32 MiB and 8 MiB. The player's global user configuration is not loaded. See [VALIDATION.md](VALIDATION.md) for diagnostic commands and validation scope.

## Open-source projects and acknowledgements

This edition uses or derives from the following projects. Original authorship and licenses are retained.

| Project | Role | License |
| --- | --- | --- |
| [Macast — xfangfang](https://github.com/xfangfang/Macast) | Tray app, DLNA, and player framework; the base of this project | [GPL v3](LICENSE) |
| [Macast-Overhauled](https://github.com/frienkie/Macast-Overhauled) | macOS plugin/player changes used as the Windows port's basis | Original component licenses |
| [Macast-plugins — xfangfang and contributors](https://github.com/xfangfang/Macast-plugins) | NVA plugin foundation | [MIT](Macast-plugins/LICENSE) |
| [mpv](https://github.com/mpv-player/mpv) | Bundled video player | GPL/LGPL according to build configuration; see packaged notices |
| [ModernZ — Samillion](https://github.com/Samillion/ModernZ) | Player controls, extended with DPI scaling and independent danmaku controls | [LGPL v2.1](mpv_ui/LICENSE.ModernZ) |
| [FFmpeg](https://ffmpeg.org/) / [libass](https://github.com/libass/libass) | Media processing and ASS subtitle/danmaku rendering | FFmpeg: GPL/LGPL according to configuration; libass: ISC |
| [Fluent System Icons — Microsoft](https://github.com/microsoft/fluentui-system-icons) | Icon source for ModernZ | MIT |
| [Material Symbols — Google](https://github.com/google/material-design-icons) | Icon source for ModernZ | Apache 2.0 |
| [Vue](https://github.com/vuejs/vue) / [Element UI](https://github.com/ElemeFE/element) / [Vue Resource](https://github.com/pagekit/vue-resource) | Advanced settings page, components, English locale, and requests | MIT |
| [Python](https://www.python.org/) / [PyInstaller](https://pyinstaller.org/) | Runtime and Windows portable packaging | Original licenses and packaging exceptions |
| [pystray](https://github.com/moses-palmer/pystray) / [Pillow](https://python-pillow.org/) | Windows tray integration and icons | See packaged notices |
| [CherryPy](https://github.com/cherrypy/cherrypy) / [cheroot](https://github.com/cherrypy/cheroot) | Local HTTP service | See packaged notices |
| [Requests](https://github.com/psf/requests) / [lxml](https://github.com/lxml/lxml) / [psutil](https://github.com/giampaolo/psutil) / [pyperclip](https://github.com/asweigart/pyperclip) | HTTP, XML, network interface enumeration, and clipboard support | See packaged notices |

ModernZ builds on mpv OSC, maoiscat/mpv-osc-modern, cyl0/ModernX, and dexeonify/ModernX. Full credits are retained in the [original ModernZ documentation](mpv_ui/ModernZ-upstream-README.md).

See [SOURCE-REVISIONS.json](SOURCE-REVISIONS.json) for base application/plugin revisions and [UPSTREAM.json](mpv_ui/UPSTREAM.json) for the pinned ModernZ revision and modifications. Full license and dependency records are indexed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the portable package's `Documentation/licenses/` directory. Each component remains under its own license.
