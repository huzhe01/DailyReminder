# AI 研究摘要邮件推送指南

本功能自动抓取 arXiv 最新论文和 YouTube 科技领袖访谈视频，整合成精美的邮件摘要发送到您的邮箱。

## 功能特点

### 📚 arXiv 论文抓取
- **大模型领域**: LLM、GPT、Transformer、BERT、RLHF、Prompt Engineering 等
- **广告领域**: CTR 预测、推荐系统、实时竞价、用户行为建模等
- 自动过滤最近 7 天的论文
- 支持多个 arXiv 分类: cs.CL、cs.LG、cs.AI、cs.IR

### 🎬 YouTube 视频获取
支持以下科技领袖的最新访谈视频:
- **Elon Musk** - Tesla、SpaceX、xAI
- **Jensen Huang** - NVIDIA CEO
- **Sam Altman** - OpenAI CEO
- **Satya Nadella** - Microsoft CEO
- **Sundar Pichai** - Google CEO
- **Mark Zuckerberg** - Meta CEO

### 📧 邮件推送
- 精美的 HTML 邮件模板
- 自动定时推送（每周一、四）
- 支持手动触发

---

## 环境变量配置

### 必需配置

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `FROM_EMAIL` | 发件人邮箱地址 | `your_email@qq.com` |
| `EMAIL_PASSWORD` | 邮箱授权码（非登录密码） | `abcdefghijklmnop` |
| `TO_EMAIL` | 收件人邮箱地址 | `recipient@gmail.com` |

### 可选配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.qq.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `YOUTUBE_API_KEY` | YouTube Data API 密钥 | 无（使用推荐列表模式） |

---

## 本地运行

### 1. 设置环境变量

```bash
# Linux/Mac
export FROM_EMAIL="your_email@qq.com"
export EMAIL_PASSWORD="your_authorization_code"
export TO_EMAIL="recipient@gmail.com"
export YOUTUBE_API_KEY="your_youtube_api_key"  # 可选

# Windows CMD
set FROM_EMAIL=your_email@qq.com
set EMAIL_PASSWORD=your_authorization_code
set TO_EMAIL=recipient@gmail.com
set YOUTUBE_API_KEY=your_youtube_api_key
```

### 2. 运行脚本

```bash
cd scripts
python research_digest_sender.py
```

---

## GitHub Actions 自动推送

### 1. 配置 Secrets

在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加以下 Secrets:

- `FROM_EMAIL`: 发件人邮箱
- `EMAIL_PASSWORD`: 邮箱授权码
- `TO_EMAIL`: 收件人邮箱
- `YOUTUBE_API_KEY`: YouTube API 密钥（可选）

### 2. 推送时间

默认每周推送两次:
- 周一 09:00（北京时间）
- 周四 09:00（北京时间）

可在 `.github/workflows/research-digest.yml` 中修改 cron 表达式。

### 3. 手动触发

在 GitHub Actions 页面，选择 "AI 研究摘要推送" 工作流，点击 "Run workflow" 手动触发。

---

## 获取 YouTube API 密钥

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3
4. 创建凭据 → API 密钥
5. 将 API 密钥添加到环境变量或 GitHub Secrets

> ⚠️ 注意: 如果不配置 YouTube API 密钥，脚本会使用推荐列表模式，提供预设的频道和搜索链接。

---

## 邮箱授权码获取

### QQ 邮箱

1. 登录 [QQ 邮箱](https://mail.qq.com)
2. 设置 → 账户 → POP3/IMAP/SMTP服务
3. 开启服务并生成授权码
4. 将授权码作为 `EMAIL_PASSWORD`

### Gmail

1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 开启两步验证
3. 应用专用密码 → 生成密码
4. 使用生成的密码作为 `EMAIL_PASSWORD`
5. 修改 SMTP 配置:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

---

## 自定义配置

### 修改关注的科技领袖

编辑 `research_digest_sender.py`:

```python
class ResearchDigestSender:
    def __init__(self):
        # 修改这里
        self.selected_leaders = ["Elon Musk", "Jensen Huang", "Sam Altman", "Sundar Pichai"]
```

### 修改论文搜索关键词

编辑 `arxiv_fetcher.py`:

```python
class ArxivFetcher:
    LLM_KEYWORDS = [
        "large language model",
        # 添加更多关键词...
    ]
    
    AD_KEYWORDS = [
        "computational advertising",
        # 添加更多关键词...
    ]
```

### 修改推送频率

编辑 `.github/workflows/research-digest.yml`:

```yaml
on:
  schedule:
    # 每天早上 9:00（北京时间）
    - cron: '0 1 * * *'
```

---

## 文件结构

```
scripts/
├── arxiv_fetcher.py           # arXiv 论文抓取模块
├── youtube_fetcher.py         # YouTube 视频获取模块
├── research_digest_sender.py  # 研究摘要邮件发送脚本
└── RESEARCH_DIGEST_GUIDE.md   # 本文档

.github/workflows/
└── research-digest.yml        # GitHub Actions 工作流
```

---

## 常见问题

### Q: 邮件发送失败？

1. 检查邮箱授权码是否正确
2. 确认 SMTP 服务已开启
3. 检查网络是否可访问 SMTP 服务器

### Q: arXiv 论文获取为空？

1. 可能是关键词匹配不到最近的论文
2. 尝试扩大搜索时间范围（修改 `filter_recent_papers` 的 `days` 参数）
3. 检查网络是否可访问 arxiv.org

### Q: YouTube API 配额不足？

1. YouTube Data API 每日有配额限制
2. 可以不配置 API 密钥，使用推荐列表模式
3. 或申请更高配额

---

## 邮件效果预览

发送的邮件包含:
- 📚 **大模型领域论文**: 标题、作者、摘要、PDF 链接
- 📊 **广告领域论文**: 标题、作者、摘要、PDF 链接  
- 🎬 **科技领袖访谈**: 视频标题、频道、描述、观看链接

采用现代化的 HTML 模板设计，在各种邮件客户端都有良好的显示效果。
