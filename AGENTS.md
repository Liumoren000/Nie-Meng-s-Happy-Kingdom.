# 接手说明

- `dist/index.html` 是游戏入口，包含 HTML、CSS、JavaScript 和内嵌像素图。离线试玩无需打包器或第三方依赖。托管发布用 `node scripts/build-worker.mjs`，云存档 API 源码在 `worker/index.mjs`，D1 SQL 在 `drizzle/`。
- `node tests/check-game.cjs` 运行本地回归测试。测试使用 Node.js 内置模块和模拟时间。
- 玩法状态通过下列 localStorage 键保存：`niemeng-kingdom-v1`。新增字段时为旧档补默认值，保留已有地块 ID、建筑、角色和资源。
- 地图共有 1,084 格，外轮廓为六边形，岛内是可放置建筑的方格。道路由布局自动生成，避开树木和山岩。中央豪宅是王座厅入口。
- `art/` 是本地美术工作文件。生成输出不会自动覆盖站点源码。复核地图时优先检查原有建筑坐标、道路连通、角色移动和缩放。
- 如需发布，请读取 `.openai/hosting.json`，沿用已有 Sites 项目和访问范围。访问凭据由 Sites 提供，切勿写入项目。
