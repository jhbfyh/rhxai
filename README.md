# 永远在线的"搭子" · 项目资料包

未成年人 AI 情感陪伴主题的滚动叙事数据报道站点，纯静态实现，第三方依赖已全部本地化，运行时零外网请求。

## 本地预览

直接双击根目录的 `index.html` 即可。若需完全等同于线上环境（GeoJSON 走 `fetch`，`file://` 下会被 CORS 拦截），在本目录启动任意静态服务器：

```bash
python -m http.server 8000
# 打开 http://127.0.0.1:8000/
```

## Cloudflare Pages 部署

上传本文件夹即可，无需构建：

1. Cloudflare Dashboard → Workers & Pages → Create → Pages → Upload assets
2. 把 `冉红鑫AI搭子资料` 整个文件夹拖进去
3. 部署完成后入口为 `/`（`index.html`）

无构建命令、无输出目录设置，根目录即站点根。`_headers` 已配置静态资源长缓存与 HTML 不缓存。

## 目录结构

```
冉红鑫AI搭子资料/                     ← 上传此文件夹即可部署
├── index.html                       序言（原 00-intro.html）
├── chapters/                        01–05 章节页
├── components/                      公共脚本（进度条、人群画布等）
├── data/                            全站数据层 window.DATA
├── styles/                          主题 token 与导航样式
├── vendor/                          本地化第三方库（不再走 CDN）
│   ├── echarts.min.js               ECharts 5.4.3
│   ├── echarts-gl.min.js            ECharts-GL 2.0.9（3D 地球仪）
│   ├── d3.min.js                    D3 7.9.0
│   └── geo/
│       ├── china.json               中国省级边界（粒子地图）
│       └── world.json               世界边界（地球仪纹理）
├── assets/                          站点图片与视频
├── deliverables/                    角色形象交付图
├── archive/                         原始大图、未引用素材、预览页
├── docs/                            结构化文档
├── tools/                           bootstrap_offline.py（离线化脚本）
└── _headers                         Cloudflare Pages 响应头配置
```

## 阅读顺序

```
index.html → 01 搭子 → 02 茧房 → 03 伤口 → 04 破茧 → 05 附录 → 回首页
```

## 文档索引

- `docs/01-项目总览.md`——选题、技术形态、依赖与运行条件
- `docs/02-目录结构.md`——目录职责与资源相对路径规则
- `docs/03-页面大纲.md`——六个页面的分节、交互与核心数字
- `docs/04-数据字典.md`——`data.js` 键结构、含义与使用状态
- `docs/05-资源清单.md`——逐文件清单：尺寸、体积、被哪一页引用

## 关键约定

1. 章节页统一引用 `../styles/theme.css`，色板只允许在该文件用 12 个 token 定义。
2. 章节页统一引用 `../components/common.js`，进场动画、数字滚动、进度条不重复实现。
3. 核心数据集中在 `data/data.js`；新增图表优先读 `window.DATA`，不要在页面里再抄一份。
4. 媒体路径一律相对当前页写 `../assets/`（首页写 `assets/`），`assets/` 必须与 `chapters/` 同级。
5. 第三方库只放在 `vendor/`，页面通过相对路径引用，禁止再引入 CDN。

## 已知事项

- `data/data.js` 中 `intro.q1–q4`、`intro.gap`、`ch1.coverNum`、`ch1.turn`、`ch3.diffs`、`ch4.accel`、`ch4.dualBar` 目前未被任何页面读取，对应数值在页面内联脚本或 HTML 中硬编码。
- `chapters/03-wound.html` 未引入 `data.js`。
- `index.html` 与 `chapters/03-wound.html` 中各保留一处 ECharts 预渲染残留（`_echarts_instance_`、`zr_0` canvas），不影响运行，重新初始化时会被覆盖。
- 站点运行时不再依赖任何外网资源；正文中的新闻与论文链接为来源标注，点击后跳转外站，不影响页面加载。
