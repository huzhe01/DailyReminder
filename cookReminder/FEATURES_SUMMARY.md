# 菜谱推送系统功能总结

## 🎉 已实现功能

### 1. 每周菜谱推送（推荐使用）

**文件**: `weekly_recipe_sender.py`

**特性**:
- ✅ 每周工作日前一天晚上8点自动推送
- ✅ 智能选择1荤1素共2个菜品
- ✅ 低油低盐健康标准（油<80g，盐<15g）
- ✅ 自动识别食材并生成购买链接
- ✅ 美团小象超市一键购买
- ✅ 精美HTML邮件排版
- ✅ 营养均衡搭配

**推送时间**:
- 周日晚8点 → 周一菜谱
- 周一晚8点 → 周二菜谱
- 周二晚8点 → 周三菜谱
- 周三晚8点 → 周四菜谱
- 周四晚8点 → 周五菜谱

**使用方法**:
```bash
cd scripts
python weekly_recipe_sender.py
```

### 2. 每日单菜推送（基础版）

**文件**: `daily_recipe_sender.py`

**特性**:
- ✅ 每个工作日推送1个健康菜品
- ✅ 低油低盐筛选
- ✅ 简洁邮件格式

**使用方法**:
```bash
python scripts/daily_recipe_sender.py
```

### 3. 食材购买链接系统

**文件**: `ingredient_links.py`

**特性**:
- ✅ 100+ 常用食材映射
- ✅ 美团小象超市链接
- ✅ 智能匹配算法
- ✅ 支持模糊匹配
- ✅ 可扩展自定义

**支持的食材类别**:
- 肉类：猪肉、牛肉、鸡肉、鱼、虾等
- 蔬菜：西兰花、青菜、胡萝卜等
- 豆制品：豆腐、豆干、腐竹等
- 蛋类：鸡蛋
- 调料：油、盐、生抽等

### 4. 邮件测试工具

**文件**: `test_email.py`

**特性**:
- ✅ 快速测试SMTP连接
- ✅ 多配置自动测试
- ✅ 详细错误诊断
- ✅ 故障排查建议

**使用方法**:
```bash
python scripts/test_email.py quick  # 快速测试
python scripts/test_email.py        # 完整测试
```

## 📁 文件结构

```
scripts/
├── weekly_recipe_sender.py      # 每周菜谱推送（主推荐）
├── daily_recipe_sender.py       # 每日单菜推送
├── ingredient_links.py          # 食材购买链接
├── test_email.py                # 邮件测试工具
├── config_example.txt           # 配置示例
├── WEEKLY_RECIPE_GUIDE.md       # 每周推送使用指南
├── README.md                    # 基础说明
├── SETUP_GUIDE.md               # 配置指南
├── TROUBLESHOOTING.md           # 故障排查
├── TEST_WEEKLY.md               # 测试指南
└── FEATURES_SUMMARY.md          # 本文件

.github/workflows/
├── weekly-recipe.yml            # 每周推送自动化
└── daily-recipe.yml             # 每日推送自动化
```

## 🚀 快速开始

### 步骤1: 配置邮箱

```bash
export FROM_EMAIL="your@qq.com"
export EMAIL_PASSWORD="your_auth_code"
export SMTP_SERVER="smtp.qq.com"
export SMTP_PORT="465"
```

### 步骤2: 测试

```bash
# 测试邮件连接
python scripts/test_email.py quick

# 测试每周推送
cd scripts
python weekly_recipe_sender.py
```

### 步骤3: 自动化（可选）

1. 配置GitHub Secrets:
   - `FROM_EMAIL`
   - `EMAIL_PASSWORD`

2. 启用GitHub Actions

3. 享受自动推送！

## 📊 功能对比

| 功能 | 每日推送 | 每周推送 |
|------|---------|---------|
| 菜品数量 | 1个 | 2个（1荤1素） |
| 推送时间 | 工作日早上8点 | 工作日前晚8点 |
| 食材链接 | ❌ | ✅ |
| 荤素搭配 | ❌ | ✅ |
| 购买清单 | ❌ | ✅ |
| 营养均衡 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 推荐程度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 推荐使用场景

### 每周推送（推荐）
- ✅ 需要提前规划第二天的菜谱
- ✅ 希望有荤素搭配建议
- ✅ 想要一键购买食材
- ✅ 注重营养均衡
- ✅ 晚上有时间采购食材

### 每日推送
- ✅ 只想每天看一个新菜品
- ✅ 自己会搭配其他菜肴
- ✅ 不需要购买链接
- ✅ 喜欢简洁的推送

## 🎯 使用建议

1. **新手推荐**: 使用每周推送
   - 提前一晚收到菜谱
   - 有时间准备食材
   - 荤素搭配更科学

2. **进阶用户**: 根据需求选择
   - 可以同时启用两个推送
   - 自定义筛选条件
   - 调整推送时间

3. **最佳实践**:
   - 晚上收到菜谱后立即查看
   - 当晚或第二天早上购买食材
   - 按照菜谱控制油盐用量
   - 如缺少食材可适当替换

## 📈 未来可能的改进

- [ ] 支持更多电商平台（盒马、叮咚买菜等）
- [ ] 添加预估价格信息
- [ ] 根据季节推荐时令菜品
- [ ] 记住用户偏好，避免重复推送
- [ ] 支持过敏食材过滤
- [ ] 添加营养成分分析
- [ ] 生成每周采购清单汇总
- [ ] 支持多人共享菜谱

## 🆘 获取帮助

- [配置指南](./SETUP_GUIDE.md)
- [故障排查](./TROUBLESHOOTING.md)
- [测试指南](./TEST_WEEKLY.md)
- [项目主页](https://github.com/Gar-b-age/CookLikeHOC)

## 📝 反馈与建议

如有问题或建议，欢迎：
- 提交 GitHub Issue
- 发送邮件反馈
- 贡献代码改进

---

祝你享受健康美味的每一餐！🍳✨

