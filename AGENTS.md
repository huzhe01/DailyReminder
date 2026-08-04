# AGENTS.md

## 项目概览

CookLikeHOC 是一个菜谱文档站点 + Python 自动化脚本仓库，包含三个相对独立的部分：

1. **VitePress 文档站点**（主要开发入口）：展示 `cookReminder/` 下的 ~200 道菜谱
2. **每日/每周菜谱邮件推送**：`scripts/daily_recipe_sender.py`、`scripts/weekly_recipe_sender.py`
3. **AI 研究摘要邮件**：`scripts/research_digest_sender.py`

## 常用命令

| 用途 | 命令 |
|------|------|
| 安装 Node 依赖 | `npm install` |
| 启动文档开发服务器 | `npm run docs:dev`（默认 http://localhost:5173） |
| 构建静态站点 | `npm run docs:build` |
| 预览构建结果 | `npm run docs:preview` |
| 安装 Python 依赖 | `pip install -r scripts/requirements.txt` |
| 测试菜谱选择逻辑 | `python3 scripts/daily_recipe_sender.py`（需 SMTP 环境变量才会发邮件） |

## Cursor Cloud specific instructions

### 主要可运行服务

- **VitePress 开发服务器**是唯一需要长期运行的本地服务。启动命令见 `package.json` 的 `docs:dev` / `start`。
- 开发服务器启动前会自动运行 `prebuild:indexes`，重新生成分类 README 索引。
- 配置在 `.vitepress/config.ts`；导航/侧边栏由 `.vitepress/navSidebar.ts` 根据顶层目录自动生成。

### Python 脚本

- 菜谱推送脚本（`daily_recipe_sender.py`、`weekly_recipe_sender.py`）仅依赖 Python 标准库，无需 `pip install`。
- 研究摘要脚本需要 `scripts/requirements.txt` 中的依赖，以及 `MODELSCOPE_API_KEY`、SMTP 相关环境变量和出站网络。
- 运行 Python 脚本时，若沙盒环境存在 `~/venv/huzhe/bin/activate`，先激活该虚拟环境。

### 已知注意事项

- **`npm run docs:build` 可能因菜谱 markdown 中图片相对路径错误而失败**（例如 `cookReminder/炸品/香酥鸡米花.md` 引用 `../images/` 而非 `../../images/`）。开发模式（`docs:dev`）可正常浏览大部分页面，但个别菜谱图片可能显示为损坏链接。
- 首页 hero 链接指向 `/炒菜/README`，实际菜谱位于 `/cookReminder/炒菜/README`；通过侧边栏导航可正常访问。
- 仓库无 lint 脚本、无测试框架、无 pre-commit hooks。
- 邮件推送与研究摘要脚本需要外部 SMTP 和 API 密钥，本地开发通常只需验证 VitePress 站点和菜谱选择逻辑即可。
