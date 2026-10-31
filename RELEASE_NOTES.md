# Windows 0.8.1

- 从本地 Macast-Overhauled macOS 源码移植，保留 NVA 0.39 协议修补、DASH 音轨与质量切换、ModernZ 蓝色主题、独立弹幕和 DPI 缩放。
- 内置 MPV 是唯一随包播放器，只附带 NVA 协议插件；标准 DLNA 内置。
- 修复 PyInstaller 资源目录、Windows IPC 名称、中文/空格路径、注册表启动项引号与错误返回、硬解禁用状态和进程回收。
- Windows 网卡改用 psutil，去掉虚构的热点地址；不再需要 netifaces 编译或 pywin32。
- D3D11 / 自动硬解，缓存上限 32+8 MiB；不读取外部 MPV 配置，不自解压，不自动联网检查应用更新。
- 修复首次动态端口绑定后的 HTTP/NVA 服务对象替换问题，恢复有效的原版 Windows 托盘图标；普通字幕避让播放器控制栏。
- 提供固定 MPV 校验、Windows 构建脚本、依赖锁定、CI、应用源码快照和离线自检。

验收结果见 `VALIDATION.md`。目标为 Win10 22H2 / Win11 x64；Win10 真机和手机端实际投屏尚待验证。
