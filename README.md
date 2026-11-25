# 聂萌的快乐王国

这是可直接运行和继续编辑的网页版项目。地图、像素素材、样式和玩法都内嵌在 `dist/index.html`。

## 在 Windows 上打开

1. 先解压 ZIP，再在 Windows 版 Codex 中打开解压后的 `niemeng-kingdom` 文件夹。
2. 双击 `start-game.cmd` 或 `dist/index.html` 试玩。游戏离线可用，无需安装依赖。
3. 在 Codex 中可以发送这句话继续开发：请先读 AGENTS.md，运行现有测试，然后从 dist/index.html 继续开发。

也可以在项目目录运行 `py -m http.server 8765 --bind 127.0.0.1`，然后在浏览器打开 `http://127.0.0.1:8765/dist/#explore`。这个方式需要 Python。

## 常用操作

- WASD / 方向键移动，鼠标左键拖地图，滚轮缩放。
- B 打开建造手册，E 操作面前的地块。点击建筑可进入管理面板。
- 地图中央的粉色梦想豪宅可进入王座厅。右上角菜单可切换全岛视图、查看任务和定位街区。

## 验证与修改

- 修改入口为 `dist/index.html`。这是游戏源码，也是可直接发布的静态文件。
- 有 Node.js 时，在项目根目录运行 `node tests/check-game.cjs`。
- `art/` 包含部分原创像素素材和地形的生成脚本。要生成参考输出，在项目根目录依次运行 `node art/dump-island.cjs`、`py art/paint-terraces-atlas.py` 和 `py art/pixel-art.py`。生成文件写入 `art-build/`。游戏读取的是 HTML 中已经嵌入的素材，更新美术时需要把对应新图替换进 HTML。

## 存档与发布

玩家进度保存在当前浏览器的本地存储中，对应游戏网址或本地文件。这个 ZIP 是项目包，未复制旧设备的存档。在线版和本地版的存档各自独立。

`.openai/hosting.json` 记录了现有 Sites 项目的 ID。运行和编辑不需要登录。要更新已有站点，需要用具有该项目访问权限的账户连接 Sites。

[已发布的试玩版](https://niemeng-happy-kingdom.supplecoast4.chatgpt.site/#explore)

## 从另一台设备继续开发

本项目的云端源码与 Sites 试玩站点绑定。把试玩网址和下列交接语句交给另一台设备上的 Codex，并确保登录的是对此 Site 有编辑权限的账号：

> 继续修改现有 Sites 项目「聂萌的快乐王国」。使用 Sites 查到项目，申请源码仓库访问凭据，并把现有源码检出到本地，先读 AGENTS.md 和运行测试。项目 ID 为 appgprj_6b05b78cec40819195df5cdf259872a8。试玩网址见上方。发布时保持原站点的私有访问范围。

每台设备可以从云端检出自己的工作副本。后续在任何设备继续修改前，先同步最新的云端源码。
