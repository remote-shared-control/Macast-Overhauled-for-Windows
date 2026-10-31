# Macast-Overhauled · Windows 插件集成版

[English](README.md) | [构建指南](BUILDING.md) | [开源许可](THIRD_PARTY_NOTICES.md)

想把手机里的视频投到 Windows 电脑上看？Macast 就是一个常驻系统托盘的接收器，视频、音乐和图片都能投。（音乐和图片的投屏实现仅基于标准 DLNA。）

这个版本从 [xfangfang 的 Macast](https://github.com/xfangfang/Macast) 出发，基于 [Macast-Overhauled 的 macOS 插件集成版](https://github.com/frienkie/Macast-Overhauled) 移植到 Windows 10 和 Windows 11。它把哔哩哔哩投屏、内置 MPV 和 [ModernZ](https://github.com/Samillion/ModernZ) 控制界面整合在一起，解压后就能用，不用再手动找播放器和插件。

这是独立维护的衍生版本。Windows 上的程序仍叫 **Macast.exe**。

## 功能

- **手机投屏**：支持标准 DLNA，以及通过 NVA 协议连接的哔哩哔哩投屏。
- **内置播放器**：MPV 与运行依赖随便携包提供，无需另外安装播放器或 Python。
- **清晰度切换**：支持从投屏端切换接口提供的 DASH 清晰度，并匹配音轨。
- **独立弹幕开关**：播放器中分别控制弹幕和普通字幕，手机弹幕开关同步生效。
- **自动缩放界面**：控件根据显示器 DPI、窗口大小和全屏状态调整尺寸，也可手动放大。
- **轻量控制界面**：采用 ModernZ 蓝色主题，不增加缩略图进程、视频滤镜或画质增强处理。
- **插件自动安装**：NVA 配套插件随程序离线安装。以后升级时，自己改过的插件也会保留。

## 安装

### 系统要求

- Windows 10 22H2 或 Windows 11，Intel / AMD **x64（64 位）**。
- 当前提供 x64 便携包，使用基础 x86-64 MPV 构建；没有制作 32 位或 ARM64 原生包。
- 手机与电脑连接同一局域网，且网络允许设备互相访问。

### 安装步骤

1. 从 [Releases 下载 **Macast-Overhauled-Windows-v0.8.2-x64.zip**](https://github.com/remote-shared-control/Macast-Overhauled-for-Windows/releases/latest/download/Macast-Overhauled-Windows-v0.8.2-x64.zip)。
2. 将 ZIP 中的**整个文件夹**解压到电脑上的固定位置。
3. 双击 **Macast.exe**，任务栏通知区域出现图标即表示应用已启动。
4. 首次使用时，如 Windows 防火墙询问，请允许 Macast 在自己的专用网络中接收连接。

保持 **Macast.exe** 与 **_internal** 文件夹在一起；只复制 EXE 无法运行。支持中文及带空格的路径。当前便携包未进行 Windows 代码签名。

### 如何获取新版

这个版本不会自动联网检查 Macast 的更新，也不会弹出上游版本提示。需要升级时，退出正在运行的 Macast，从本项目获取新的 ZIP 并解压完整文件夹，再启动新版。随程序附带、未经修改的插件会在下次启动时更新；你自己修改的插件会保留。

## 使用方法

### 哔哩哔哩投屏

1. 右键点击 Macast 托盘图标，在设置中确认选择 **NVA Protocol** 和 **MPV Renderer**（首次启动的默认组合）。
2. 在手机哔哩哔哩客户端中打开视频，点击投屏按钮。
3. 从设备列表选择 **我的小电视**。
4. 使用手机控制播放、暂停、进度与可用清晰度，也可在电脑播放器中操作。

可选清晰度由视频、接口返回结果和账号权限决定；某一清晰度没有出现时，本应用无法额外解锁。

### 普通 DLNA 投屏

在 Macast 中选择 **DLNA Protocol**，然后在支持 DLNA 的手机应用中搜索并选择 Macast 设备。设备名以 Macast 的当前设置为准。默认的 NVA 协议也继承了 DLNA，遇到客户端兼容问题时可切换到纯 DLNA 协议。

### 播放器操作

播放器和设置界面使用英语，视频标题、字幕正文和弹幕保留原语言。将鼠标移到播放器下方可显示控制栏。

| 控件 | 功能 |
| --- | --- |
| 播放 / 暂停按钮 | 控制当前视频 |
| 进度条 | 跳转播放位置 |
| 音量按钮 | 调整音量或静音 |
| **Subtitles** 字幕图标 | 选择普通字幕轨；选择 **Off** 关闭字幕 |
| **Danmaku** 气泡图标 | 单独开启或关闭弹幕；有弹幕可用时显示 |
| 全屏按钮 | 切换全屏显示 |

弹幕和字幕使用独立开关。关闭字幕不会关闭弹幕；手机上的弹幕开关也会同步到播放器。若视频没有提供普通字幕，字幕按钮可能不可用。普通字幕会避让显示中的底部控制栏，弹幕保持独立位置。

### 大屏幕和高 DPI 显示器

打开 Macast 设置中的 **Player UI Size**：

| 选项 | 效果 |
| --- | --- |
| **Automatic (DPI)** | 随显示器 DPI、窗口大小和全屏状态自动缩放 |
| **Automatic + 25%** | 在自动缩放基础上放大 25% |
| **Automatic + 50%** | 在自动缩放基础上放大 50% |

设置即时生效，无需重启播放器。

## 插件与内置播放器

首次启动时，NVA 插件自动安装到当前用户的配置目录。升级后，未经修改的内置插件会自动更新，替换前保留备份；自定义修改不会被覆盖。

| 组件 | 用途 |
| --- | --- |
| Nirvana / NVA Protocol | 哔哩哔哩投屏协议，源码见 [Macast-plugins/nirvana](Macast-plugins/nirvana/) |
| DLNA Protocol | 应用内置的标准 DLNA 协议 |
| MPV Renderer | 唯一随包播放器，配套 ModernZ 界面、独立弹幕和字幕控制 |

Windows 版只使用内置 MPV，不附带 PotPlayer 或其他外部播放器集成。默认使用 Windows D3D11 输出和自动硬解；遇到显卡驱动问题时，可从设置中关闭 **Hardware Decode**。

## 常见问题

### 手机搜不到设备？

确认两台设备处于同一局域网；检查 Windows 网络类型和防火墙是否允许 Macast 在专用网络中接收连接。访客网络、无线客户端隔离和部分 VPN 可能阻止发现设备。B 站投屏还需确认选中了 **NVA Protocol**。

### 选了设备，却没有打开播放器？

确认播放器选中 **MPV Renderer**，且没有移动或删除便携包中的 **_internal** 文件夹。重新选择视频发起投屏，并检查 **Open Config Directory** 中的 `application.log`。

### 1080P 怎么选不了？

先确认手机端该视频和账号具备相应清晰度权限。实际可选画质受接口返回结果影响；网络错误、媒体地址失效或客户端协议变化也可能影响播放。

### 切换视频为什么要等一会儿？

切换时播放器会清除旧画面并加载新视频。清晰度与播放地址获取、网络传输、解码准备和缓冲均需要时间；无法保证零等待。若等待异常，可通过配置目录中的 `latency.log` 查看各阶段耗时。

### 如何修改配置或反馈问题

菜单 **Open Config Directory** 可打开：

```text
%LOCALAPPDATA%\Macast-Overhauled
```

其中 `protocol/` 保存 NVA 插件，`bundled-plugin-backups/` 保存升级备份；`application.log` 和 `latency.log` 滚动保存。可在托盘设置中自行启用当前用户登录启动，默认关闭。

反馈问题时，请提供 Windows 版本、CPU / 显卡、所用协议、手机客户端版本、复现步骤及相关日志。分享日志前移除账号信息、令牌和完整媒体地址。请说明使用的是本衍生版本，便于与上游版本区分。

## 使用前知道这些就好

- 当前包面向 Windows 10 22H2 / Windows 11 x64。已在 Windows 11 上完成 37 项回归测试及本地渲染、NVA 握手和便携路径检查；Windows 10 真机、手机实际投屏及不同显卡 / 多屏 DPI 仍需实机验收。
- 多段 `durl` 视频暂不支持；DRM、特殊音轨及部分客户端协议组合可能无法播放。
- 新版客户端或服务接口变化可能影响投屏。账号和内容访问权限由媒体服务决定。

## 从源码构建

参阅 [BUILDING.md](BUILDING.md)。保留 `Macast-plugins/` 插件目录，在 Windows x64 上使用 Python 3.12 构建。便携包中附有双语说明、许可证及 `Documentation/Macast-Windows-Source-v0.8.2.zip` 修改源码快照。

采用目录式便携打包，避免每次启动自解压；媒体缓存上限为前向 32 MiB、后向 8 MiB，不读取用户独立 MPV 的全局配置。诊断和测试范围见 [VALIDATION.md](VALIDATION.md)。

## 开源项目与致谢

本项目使用或衍生自以下开源项目，原作者署名和许可予以保留：

| 项目 | 在本项目中的用途 | 许可 |
| --- | --- | --- |
| [Macast — xfangfang](https://github.com/xfangfang/Macast) | 托盘应用、DLNA 与播放器框架，本项目的基础 | [GPL v3](LICENSE) |
| [Macast-Overhauled](https://github.com/frienkie/Macast-Overhauled) | 本次 Windows 移植所依据的 macOS 插件与播放器修改 | 各组件原有许可 |
| [Macast-plugins — xfangfang 及贡献者](https://github.com/xfangfang/Macast-plugins) | NVA 协议插件基础 | [MIT](Macast-plugins/LICENSE) |
| [mpv](https://github.com/mpv-player/mpv) | 内置视频播放器 | 按构建配置适用 GPL/LGPL，见随包原始许可 |
| [ModernZ — Samillion](https://github.com/Samillion/ModernZ) | 播放器控制界面，本项目增加 DPI 缩放与独立弹幕控制 | [LGPL v2.1](mpv_ui/LICENSE.ModernZ) |
| [FFmpeg](https://ffmpeg.org/) / [libass](https://github.com/libass/libass) | 媒体处理与 ASS 字幕、弹幕渲染 | FFmpeg 按构建配置适用 GPL/LGPL；libass 为 ISC |
| [Fluent System Icons — Microsoft](https://github.com/microsoft/fluentui-system-icons) | ModernZ 图标字体来源之一 | MIT |
| [Material Symbols — Google](https://github.com/google/material-design-icons) | ModernZ 图标字体来源之一 | Apache 2.0 |
| [Vue](https://github.com/vuejs/vue) / [Element UI](https://github.com/ElemeFE/element) / [Vue Resource](https://github.com/pagekit/vue-resource) | 高级设置页面、组件、英语语言包及请求处理 | MIT |
| [Python](https://www.python.org/) / [PyInstaller](https://pyinstaller.org/) | 应用运行时与 Windows 便携打包 | 见各项目原始许可与打包例外 |
| [pystray](https://github.com/moses-palmer/pystray) / [Pillow](https://python-pillow.org/) | Windows 托盘集成与图标 | 见随包原始许可 |
| [CherryPy](https://github.com/cherrypy/cherrypy) / [cheroot](https://github.com/cherrypy/cheroot) | 本地 HTTP 服务 | 见随包原始许可 |
| [Requests](https://github.com/psf/requests) / [lxml](https://github.com/lxml/lxml) / [psutil](https://github.com/giampaolo/psutil) / [pyperclip](https://github.com/asweigart/pyperclip) | 网络请求、XML、网卡枚举与剪贴板支持 | 见随包原始许可 |

ModernZ 继承了 mpv OSC、maoiscat/mpv-osc-modern、cyl0/ModernX 和 dexeonify/ModernX 的工作，完整上游致谢见 [ModernZ 原始文档](mpv_ui/ModernZ-upstream-README.md)。

Macast 和插件的基础版本见 [SOURCE-REVISIONS.json](SOURCE-REVISIONS.json)；ModernZ 固定版本与修改记录见 [UPSTREAM.json](mpv_ui/UPSTREAM.json)。完整许可与依赖记录见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)，以及便携包 `Documentation/licenses/` 中的记录。各组件继续遵守各自许可证。
