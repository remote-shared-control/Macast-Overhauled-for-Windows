# Windows 验收记录

构建环境：Windows 11 build 26200，CPython 3.12.14 x64。播放器：MPV v0.41.0-1227-ge471496c5，FFmpeg N-127893-g9a861e968。

- 已继承原来的 26 项协议/播放参数回归测试。
- 增加 Windows 资源定位、工作目录无关性、活动网卡筛选、单实例释放、插件定制保留与升级备份、NVA 单插件打包、Unicode 路径下真实 MPV/ModernZ 检查。
- 打包后通过 `Macast.exe --diagnose` 验证真实命名管道、ModernZ 脚本、弹幕属性、资源校验和以及线程/进程退出。
- 最终回归套件为 37 项；构建脚本必须全部通过才会生成发行 ZIP。

尚待实际设备验证：Windows 10 22H2、手机 B 站/NVA 与其他 DLNA 客户端、Wi-Fi 跨设备发现/防火墙、多屏混合 DPI、不同 GPU 硬解、4K 长时间播放。测试中的模拟协议交互不构成这些项目的实测。

## 集成检查结果

- 最终 37 项回归测试已全部通过，包含真实 MPV、托盘及 NVA 服务检查。
- 冻结程序的 ModernZ/弹幕离线自检和实际托盘 + HTTP + NVA SETUP 握手均通过，线程和 MPV 子进程正常退出。
- 将完整便携目录搬移到含中文和空格的路径，并从 PATH 去掉 Python/MPV 后，离线自检和完整服务检查均通过。
- `python tools/verify_player.py` 用随包 MPV 渲染本地 960×540 静音测试图，确认 D3D11 输出、中文普通字幕与 ASS 弹幕分别可见且开关互不影响。普通字幕会避让底部控制栏；明确固定 secondary-sub-pos=100，防止主字幕位移带动弹幕。该检查短暂显示播放器窗口，无网络媒体请求。
- 测试图截图在 `build/player-check/modernz-windows.png`，已人工查看；相同截图与参数记录随产物保存在 Documentation/Player-check。
- 冻结服务就绪时的单次快照：接收器工作集约 60 MiB，空闲 MPV 约 25 MiB。此读数不代表视频播放峰值。启动计时记录的范围见 JSON；不作为不同电脑的冷启动承诺。
- 修复了继承图标损坏，以及首次分配端口后替换运行中 HTTP server 导致 NVA/退出异常的问题。只更新发现端口，保留设备标识。

复核：`python -m pytest tests Macast-plugins/tests -q`；`Macast.exe --diagnose report.json`；开发者可用 `Macast.exe --config-dir <empty-dir> --smoke-test report.json` 进行完整本地服务检查，后者短暂运行托盘及局域网服务。
