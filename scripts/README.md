# 每日健康菜品推送脚本

## 功能说明

这个脚本可以每个工作日自动从菜谱库中筛选低油低盐的健康菜品，并通过邮件发送到指定邮箱。

## 功能特点

- 🥗 **健康筛选**: 自动筛选低油低盐的健康菜品
- 📅 **工作日推送**: 每个工作日（周一至周五）自动推送
- 📧 **邮件推送**: 精美的HTML格式邮件
- 🎲 **随机选择**: 每天推荐不同的菜品

## 筛选标准

脚本会优先推荐以下类型的菜品：

1. **蒸菜**: 保留营养，少油健康
2. **烫菜**: 水煮清淡
3. **汤类**: 清淡鲜美
4. **凉拌**: 少油清爽
5. **清炒类**: 用油量少于50g的炒菜
6. **含健康关键词**: 包含"清炒"、"清蒸"、"水煮"、"汆烫"等关键词的菜品

## 配置说明

### 1. 环境变量

需要设置以下环境变量：

```bash
SMTP_SERVER=smtp.qq.com        # SMTP服务器地址
SMTP_PORT=465                  # SMTP端口（SSL，QQ邮箱推荐）
FROM_EMAIL=your@email.com      # 发件人邮箱
EMAIL_PASSWORD=your_password   # 邮箱授权码（不是登录密码）
```

### 2. GitHub Actions 配置

如果使用 GitHub Actions 自动运行，需要在仓库设置中添加以下 Secrets：

1. 进入仓库 Settings -> Secrets and variables -> Actions
2. 添加以下 secrets：
   - `FROM_EMAIL`: 发件人邮箱地址
   - `EMAIL_PASSWORD`: 邮箱授权码

### 3. 获取邮箱授权码

#### QQ邮箱
1. 登录 QQ 邮箱
2. 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启"IMAP/SMTP服务"
4. 生成授权码并保存

#### 其他邮箱
- 163邮箱: 设置 -> POP3/SMTP/IMAP -> 开启并获取授权码
- Gmail: 使用应用专用密码（需要开启两步验证）

## 本地运行

```bash
# 设置环境变量
export FROM_EMAIL="your@email.com"
export EMAIL_PASSWORD="your_password"
export SMTP_SERVER="smtp.qq.com"
export SMTP_PORT="465"

# 运行脚本
python scripts/daily_recipe_sender.py
```

## GitHub Actions 定时任务

脚本已配置为每个工作日北京时间早上8点自动运行。

如果需要修改运行时间，编辑 `.github/workflows/daily-recipe.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * 1-5'  # 北京时间早上8点 = UTC时间0点
```

Cron 表达式说明：
- `0 0 * * 1-5`: 周一到周五 UTC 0:00（北京时间 8:00）
- `0 2 * * 1-5`: 周一到周五 UTC 2:00（北京时间 10:00）

**注意**: GitHub Actions 使用 UTC 时区，北京时间需要减8小时。

## 手动触发

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "每日健康菜品推送" workflow
3. 点击 "Run workflow" 按钮

## 邮件示例

邮件包含以下内容：
- 菜品名称和分类
- 配料清单
- 制作步骤
- 精美的HTML排版
- 项目链接

## 故障排查

### 邮件发送失败
1. 检查邮箱授权码是否正确
2. 确认SMTP服务器地址和端口
3. 检查邮箱是否开启SMTP服务
4. 查看GitHub Actions日志了解详细错误

### 未收到邮件
1. 检查垃圾邮件文件夹
2. 确认收件人邮箱地址正确
3. 查看GitHub Actions运行状态

## 自定义配置

### 修改收件人邮箱

编辑 `scripts/daily_recipe_sender.py` 文件，修改最后的目标邮箱：

```python
target_email = "huzhe01@foxmail.com"  # 修改为你的邮箱
```

### 调整筛选条件

可以在 `is_low_oil_salt` 方法中调整油盐的阈值：

```python
is_low_oil = total_oil < 50  # 修改油的上限
is_low_salt = total_salt < 10  # 修改盐的上限
```

---

# 🔬 AI 研究摘要邮件推送

## 功能说明

自动抓取 arXiv 最新论文和 YouTube 科技领袖访谈视频，整合成精美的邮件摘要发送。

## 功能特点

- 📚 **arXiv 论文**: 大模型 (LLM/GPT/Transformer) 和广告领域 (CTR/推荐系统) 最新论文
- 🎬 **YouTube 视频**: Elon Musk、Jensen Huang、Sam Altman 等科技领袖访谈
- 📧 **精美邮件**: 现代化 HTML 模板设计
- ⏰ **自动推送**: 每周一、四自动推送

## 快速开始

```bash
# 设置环境变量
export FROM_EMAIL="your@email.com"
export EMAIL_PASSWORD="your_authorization_code"
export TO_EMAIL="recipient@email.com"
export YOUTUBE_API_KEY="your_api_key"  # 可选

# 运行脚本
cd scripts
python research_digest_sender.py
```

## 详细文档

请查看 [RESEARCH_DIGEST_GUIDE.md](./RESEARCH_DIGEST_GUIDE.md)

---

## 许可证

本脚本基于原项目的许可证发布。

