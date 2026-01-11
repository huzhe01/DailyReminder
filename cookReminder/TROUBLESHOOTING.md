# 故障排查指南

## ❌ 错误：535 Login fail

### 错误信息
```
535 Login fail. Account is abnormal, service is not open, password is incorrect, 
login frequency limited, or system is busy.
```

### 解决步骤

#### 步骤1：重新生成授权码

1. 登录 [QQ邮箱](https://mail.qq.com)
2. 点击**设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 点击**生成授权码**（或重新生成）
5. 按提示发送短信验证
6. **立即复制**新的授权码，确保：
   - ✅ 不包含空格
   - ✅ 16位字母组合
   - ✅ 全部小写
   - ✅ 复制完整

#### 步骤2：先在网页登录确认

1. 打开 [QQ邮箱](https://mail.qq.com)
2. 用QQ号和QQ密码登录
3. 检查是否有"异常登录"或"安全验证"提示
4. 完成所有验证

#### 步骤3：等待5-10分钟

如果多次尝试失败，QQ会临时限制登录，请等待5-10分钟后再试。

#### 步骤4：使用新授权码测试

```bash
# 设置新的授权码
export FROM_EMAIL="545088576@qq.com"
export EMAIL_PASSWORD="新的授权码"  # 替换为刚生成的授权码
export SMTP_SERVER="smtp.qq.com"
export SMTP_PORT="465"

# 测试
python scripts/test_email.py quick
```

---

## 🔄 备选方案：使用163邮箱

如果QQ邮箱持续有问题，建议改用163邮箱（更稳定）：

### 1. 开启163邮箱SMTP服务

1. 登录 [163邮箱](https://mail.163.com)
2. 设置 → POP3/SMTP/IMAP
3. 开启 **SMTP服务**
4. 生成**客户端授权密码**（这就是授权码）

### 2. 使用163邮箱配置

```bash
export FROM_EMAIL="your_email@163.com"
export EMAIL_PASSWORD="163邮箱的授权码"
export SMTP_SERVER="smtp.163.com"
export SMTP_PORT="465"

python scripts/test_email.py quick
```

### 3. 修改脚本配置

编辑 `scripts/daily_recipe_sender.py`，修改默认值：

```python
smtp_server = os.getenv('SMTP_SERVER', 'smtp.163.com')  # 改为163
smtp_port = int(os.getenv('SMTP_PORT', '465'))
```

---

## 🔄 备选方案：使用Gmail

### 1. 开启Gmail两步验证和应用专用密码

1. 访问 [Google账户](https://myaccount.google.com/)
2. 安全性 → 两步验证（开启）
3. 应用专用密码 → 生成新密码
4. 选择"邮件"和你的设备

### 2. 使用Gmail配置

```bash
export FROM_EMAIL="your_email@gmail.com"
export EMAIL_PASSWORD="应用专用密码"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"  # Gmail使用587端口

python scripts/test_email.py quick
```

---

## 📋 常见问题

### Q: 确定服务已开启，为什么还是失败？

A: 即使服务显示"已开启"，授权码也可能存在以下问题：
- 授权码已过期（较久未使用）
- 授权码被系统撤销（安全原因）
- 复制时包含了不可见字符
- **解决方法：重新生成新的授权码**

### Q: 每次都显示"Login fail"？

A: 可能是以下原因：
1. **授权码不是最新的** → 重新生成
2. **账户有异常** → 登录网页版确认
3. **被临时限制** → 等待10分钟
4. **网络环境问题** → 换网络（如手机热点）

### Q: 如何确认授权码格式正确？

A: 正确的QQ邮箱授权码特征：
- 16位字符
- 全部小写字母
- 无空格、无特殊字符
- 示例格式：`abcdefghijklmnop`

可以运行此命令检查：
```bash
echo "授权码长度: ${#EMAIL_PASSWORD}"
echo "授权码内容: $EMAIL_PASSWORD"
```
应该显示长度为16。

### Q: 所有方法都试过了还是不行？

A: 尝试以下终极方案：

1. **完全重置QQ邮箱SMTP设置**
   - 关闭所有SMTP相关服务
   - 等待1小时
   - 重新开启并生成新授权码

2. **更换邮箱服务**
   - 163邮箱（推荐，稳定性好）
   - Gmail（需要梯子）
   - 阿里云邮箱
   - Outlook邮箱

3. **检查系统环境**
   ```bash
   # 测试网络连通性
   telnet smtp.qq.com 465
   # 或
   nc -zv smtp.qq.com 465
   ```

---

## ✅ 成功标志

当看到以下输出时，表示配置成功：

```
✅ 连接和登录成功！
```

然后就可以正常使用邮件推送功能了！

