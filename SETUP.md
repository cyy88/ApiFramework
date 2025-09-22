# 项目安装和配置指南

## 环境准备

### 系统要求
- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- Redis 5.0 或更高版本
- Allure 命令行工具

### 安装 Python 依赖
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 安装 Allure 命令行工具

#### Windows
```bash
# 使用 Scoop
scoop install allure

# 或者下载二进制文件
# 1. 从 https://github.com/allure-framework/allure2/releases 下载
# 2. 解压到任意目录
# 3. 将 bin 目录添加到 PATH 环境变量
```

#### macOS
```bash
# 使用 Homebrew
brew install allure
```

#### Linux
```bash
# 下载并安装
wget https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz
tar -zxvf allure-2.24.0.tgz
sudo mv allure-2.24.0 /opt/allure
echo 'export PATH="/opt/allure/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 配置文件设置

### 1. 环境配置文件
复制并修改环境配置文件：
```bash
cp config/env_yftest.yml config/env_local.yml
```

编辑 `config/env_local.yml`：
```yaml
common:
  username: 
  - your_username1
  - your_username2
  password:
  - your_password1
  - your_password2
  tenant_id:
  - your_tenant_id1
  - your_tenant_id2

http:
  factory: https://your-api-domain.com

db:
  host: your-db-host
  password: your-db-password
  port: 3306
  user: your-db-user
  db: your-database-name

redis:
  host: your-redis-host
  password: your-redis-password
  port: 6379
```

### 2. 邮件配置（可选）
创建 `config/email_config.yml`：
```yaml
email:
  enabled: true  # 是否启用邮件发送
  sender: your-email@example.com
  password: your-email-password  # 邮箱授权码
  smtp_server: smtp.example.com
  smtp_port: 465
  receivers:
    - recipient1@example.com
    - recipient2@example.com
  subject_prefix: "API自动化测试报告"
```

## 数据库设置

### 创建测试数据库
```sql
-- 创建数据库
CREATE DATABASE your_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'test_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON your_test_db.* TO 'test_user'@'%';
FLUSH PRIVILEGES;
```

### 导入测试数据（如果有）
```bash
mysql -h your-host -u test_user -p your_test_db < test_data.sql
```

## Redis 设置

### 基本配置
确保 Redis 服务正在运行，并且可以通过配置的主机和端口访问。

### 测试连接
```python
import redis
r = redis.Redis(host='your-redis-host', port=6379, password='your-password')
r.ping()  # 应该返回 True
```

## 验证安装

### 1. 检查 Python 环境
```bash
python --version  # 应该显示 3.8+
pip list | grep pytest  # 检查 pytest 是否安装
```

### 2. 检查 Allure
```bash
allure --version  # 应该显示版本信息
```

### 3. 运行测试验证
```bash
# 运行单个测试用例验证环境
pytest testcases/buyer/test_001_select_school.py -v

# 运行完整测试套件
python run.py local  # 使用 local 环境配置
```

## 常见问题解决

### 1. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. Allure 命令找不到
- 确保 Allure 已正确安装并添加到 PATH
- 重启终端或重新加载环境变量

### 3. 数据库连接失败
- 检查数据库服务是否运行
- 验证主机、端口、用户名、密码是否正确
- 检查防火墙设置

### 4. Redis 连接失败
- 检查 Redis 服务是否运行
- 验证主机、端口、密码是否正确
- 检查网络连接

### 5. SSL 证书错误
如果遇到 SSL 证书验证错误，可以在代码中设置：
```python
# 在 common/client.py 中已经设置了 verify=False
# 如果仍有问题，可以设置环境变量
export PYTHONHTTPSVERIFY=0
```

## 开发环境设置

### 1. 代码格式化工具
```bash
pip install black flake8 isort
```

### 2. 预提交钩子
```bash
pip install pre-commit
pre-commit install
```

### 3. IDE 配置
推荐使用 PyCharm 或 VSCode，并安装以下插件：
- Python
- Pytest
- YAML

## 性能优化建议

### 1. 并发执行
在 `pytest.ini` 中调整并发数：
```ini
addopts = -sv --alluredir ./report/data --clean-alluredir -n 4 --dist=each
```

### 2. 数据库连接池
考虑使用连接池来优化数据库连接：
```python
# 在 mysql_basic/mysql_util.py 中可以添加连接池支持
```

### 3. 缓存优化
合理使用 Redis 缓存来减少重复的数据库查询。

## 部署到 CI/CD

### GitHub Actions 示例
创建 `.github/workflows/test.yml`：
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python run.py ci
```

## 监控和告警

### 1. 测试结果监控
可以集成 Grafana 或其他监控工具来跟踪测试结果趋势。

### 2. 失败告警
配置邮件或 Slack 通知来及时获得测试失败信息。

## 安全注意事项

1. **不要在代码中硬编码敏感信息**
2. **使用环境变量或加密配置文件**
3. **定期更新依赖包**
4. **限制数据库和 Redis 的访问权限**
5. **在生产环境中使用 HTTPS**

## 获取帮助

如果在安装或配置过程中遇到问题：
1. 查看项目的 README.md 文件
2. 检查 GitHub Issues
3. 联系项目维护者
