# Windows 构建指南

使用 Windows 10/11 x64 和 CPython 3.12 x64；在项目根目录执行。构建依赖固定在 `requirements/windows-lock.txt`，精简运行依赖清单见 `requirements/windows.txt`。构建时联网下载，打包后的程序不依赖本机 Python 或 PATH 中的 MPV。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/windows-lock.txt
.\.venv\Scripts\python.exe tools/fetch_mpv.py
.\.venv\Scripts\python.exe tools/build_windows.py
```

也可运行 `powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1`，该选项只影响本次脚本进程。
Windows 构建使用本指南中的脚本和 `Macast-Windows.spec`；macOS 打包脚本不在本仓库的 Windows 发布内容中。

`fetch_mpv.py` 固定使用 shinchiro 的 baseline x64 `20261021 / e471496c56` 构建，并验证下载 SHA256；不会选择要求较新 CPU 指令集的 v3/v4 包。解压优先使用 7-Zip（GitHub Windows runner 已安装），也可使用支持 LZMA 的新版 Windows `tar`；旧版 `tar` 若提示不支持 LZMA，请安装 7-Zip 后重试。7-Zip 仅是构建工具，便携程序运行不需要它。下载包中的安装器和更新器不执行、不打包。Windows 10/11 使用系统 D3DCompiler_47，不打包旧版 _43 DLL。

如果已有自备的 MPV 目录，可运行 `python tools/build_windows.py --mpv-dir C:/path/to/mpv`。该目录需要 `mpv.exe` 和可复核的许可/来源资料；推荐使用脚本固定的单体构建。自行替换 MPV 后需重新完成全部验收。

构建依次：生成仅含 NVA 的离线插件 → 回归测试 → PyInstaller one-folder → 打包后真实 IPC/ModernZ 自检 → 收集文档、许可与应用源码快照 → ZIP 与 SHA256。
产物：`dist/Macast-Overhauled-Windows/Macast.exe` 和 `dist/Macast-Overhauled-Windows-v0.8.2-x64.zip`。

构建输出不启用 UPX，不执行管理员安装、系统 MPV 注册、开机启动修改或防火墙规则修改。首次运行的 Windows 网络访问询问由系统处理。

## 验证

```powershell
.\.venv\Scripts\python.exe -m pytest tests Macast-plugins/tests -q
.\dist\Macast-Overhauled-Windows\Macast.exe --diagnose build/frozen-diagnostic.json
```

集成测试需要本机 loopback socket 和命名管道权限，受限制的容器可能阻止这些操作。测试通过表示对应功能检查通过，不等于手机、显卡或 Windows 10 实机测试通过。

GitHub Actions 配置为 `.github/workflows/build-windows.yml`，在 `windows-2022` 构建并上传产物，不自动发布 Release。仓库仅发布 Windows workflow；旧平台构建文件保留在本地参考目录，未加入 Windows 发布内容。

当前便携包使用 CPython 3.12.14 x64 在独立 `.venv` 构建；开发者可使用标准 CPython 3.12 安装。完整应用修改源码随产物的 `Documentation/Macast-Windows-Source-v0.8.2.zip` 提供。

`fetch_mpv.py` 同时下载并校验官方 LunarG runtime components ZIP，仅提取 x64 `vulkan-1.dll` 与原始许可，不运行安装器、SDK 或驱动。该 DLL 是当前 MPV 的静态导入依赖，即使采用 D3D11 输出也需要随包提供；可自备的 MPV 目录也需包含它。
