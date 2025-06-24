# API 对象框架 (API Object Framework)

## 项目简介

这是一个基于 Python 的 API 自动化测试框架，专门为"洁兔"校园超市后台管理系统设计。该框架采用面向对象的设计模式，提供了完整的 API 测试解决方案，包括学校管理、商品管理等核心业务模块的自动化测试。

## 主要功能

### 核心业务模块
- **学校管理模块**：支持学校的创建、查询、更新等操作
- **商品管理模块**：支持商品的添加、删除、查询等操作
- **用户认证模块**：支持多租户登录认证和权限管理

### 测试框架特性
- **多环境支持**：支持测试、预发布等多种环境配置
- **并发测试**：支持多线程并发执行测试用例
- **数据驱动**：支持 YAML、Excel 等多种数据源
- **报告生成**：集成 Allure 生成详细的测试报告
- **日志记录**：完整的请求响应日志记录
- **邮件通知**：自动发送测试报告到指定邮箱

## 项目结构

```
apiobjectframework/
├── api/                    # API 接口封装
│   ├── base_api.py        # 基础 API 类
│   ├── factory/           # 工厂端 API
│   │   ├── school/        # 学校管理相关接口
│   │   ├── goods/         # 商品管理相关接口
│   │   └── login_apis.py  # 登录接口
│   └── basic/             # 基础接口
├── testcases/             # 测试用例
│   └── buyer/             # 买家端测试用例
├── common/                # 公共工具类
│   ├── client.py          # HTTP 客户端
│   ├── logger.py          # 日志工具
│   ├── json_util.py       # JSON 处理工具
│   └── file_load.py       # 文件加载工具
├── config/                # 配置文件
│   ├── env_yftest.yml     # 测试环境配置
│   ├── common.yml         # 通用配置
│   ├── http.yml           # HTTP 配置
│   ├── db.yml             # 数据库配置
│   └── redis.yml          # Redis 配置
├── data/                  # 测试数据
│   ├── data.yml           # YAML 格式测试数据
│   └── add_school_data.xlsx # Excel 格式测试数据
├── utils/                 # 工具类
│   └── AllureUtils.py     # Allure 报告工具
├── mysql_basic/           # MySQL 数据库操作
├── redis_basic/           # Redis 操作
├── report/                # 测试报告
├── logs/                  # 日志文件
├── run.py                 # 主运行脚本
├── conftest.py            # pytest 配置
└── pytest.ini            # pytest 配置文件
```

## 技术栈

- **测试框架**：pytest
- **HTTP 客户端**：requests
- **报告生成**：allure-pytest
- **数据处理**：PyYAML, openpyxl, jsonpath
- **数据库**：MySQL (pymysql)
- **缓存**：Redis
- **并发执行**：pytest-xdist
- **失败重试**：pytest-rerunfailures

## 快速开始

### 环境要求
- Python 3.8+
- MySQL 数据库
- Redis 缓存

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境
1. 修改 `config/env_yftest.yml` 中的环境配置
2. 配置数据库连接信息
3. 配置 Redis 连接信息
4. 配置邮件服务器信息

### 运行测试
```bash
# 使用默认环境（yftest）
python run.py

# 指定环境运行
python run.py yftest

# 运行特定测试用例
pytest testcases/buyer/test_001_select_school.py -v
```

### 查看报告
测试完成后，Allure 报告会自动启动并在浏览器中打开。报告链接会显示在控制台输出中。

## 配置说明

### 环境配置 (config/env_yftest.yml)
```yaml
common:
  username: [sanya, liyang]  # 测试用户
  password: [jt123456, jt123456]  # 用户密码
  tenant_id: [422, 421]  # 租户ID

http:
  factory: https://admin.test.jietukj.com  # API 基础URL

db:
  host: your-db-host
  user: your-username
  password: your-password
  db: your-database

redis:
  host: your-redis-host
  password: your-password
  port: 6379
```

### pytest 配置 (pytest.ini)
- 支持并发执行（2个线程）
- 自动生成 Allure 报告
- 支持失败重试
- 详细的日志输出

## API 接口说明

### 学校管理接口
- `POST /admin-api/tcom/school/create` - 创建学校
- `GET /admin-api/tcom/school/page` - 查询学校列表
- `PUT /admin-api/tcom/school/update` - 更新学校信息
- `GET /admin-api/tcom/school/get` - 获取学校详情

### 商品管理接口
- `POST /admin-api/tcom/product/create` - 创建商品
- `DELETE /admin-api/tcom/product/delete` - 删除商品
- `PUT /admin-api/tcom/product/update` - 更新商品

### 认证接口
- `POST /admin-api/system/auth/login` - 用户登录
- `GET /admin-api/system/tenant/get-id-by-name` - 获取租户ID

## 测试数据管理

框架支持多种测试数据格式：

1. **YAML 格式** (`data/data.yml`)
2. **Excel 格式** (`data/add_school_data.xlsx`)
3. **代码内嵌数据**

### 数据驱动示例
```python
@pytest.mark.parametrize('casename,school_name,school_type,isHaveCard,school_address,school_lonlat,expect_status', 
                         load_yaml_file(data_yaml)['添加学校接口'])
def test_add_school(self, casename, school_name, school_type, isHaveCard, school_address, school_lonlat, expect_status):
    # 测试逻辑
```

## 日志和报告

### 日志功能
- 自动记录所有 HTTP 请求和响应
- 支持不同日志级别
- 按日期和环境分类存储

### Allure 报告
- 详细的测试执行报告
- 支持步骤展示和截图
- 自动生成趋势图表
- 支持邮件发送报告链接

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 项目改进建议

基于对当前项目的分析，以下是建议的改进方向：

### 1. 代码质量改进
- **添加类型注解**：为函数参数和返回值添加类型提示，提高代码可读性
- **完善异常处理**：增加更细粒度的异常处理和错误信息
- **代码规范**：统一代码风格，添加 flake8、black 等代码格式化工具
- **文档字符串**：为所有类和方法添加详细的文档字符串

### 2. 测试框架增强
- **断言库升级**：考虑使用 pytest-assume 或自定义断言方法
- **测试数据隔离**：实现测试数据的自动清理和隔离机制
- **Mock 支持**：添加对外部依赖的 Mock 支持
- **性能测试**：集成性能测试功能

### 3. 配置管理优化
- **环境变量支持**：支持通过环境变量覆盖配置
- **配置验证**：添加配置文件的格式验证
- **敏感信息加密**：对密码等敏感信息进行加密存储
- **配置模板**：提供配置文件模板和示例

### 4. 监控和可观测性
- **指标收集**：添加测试执行指标收集
- **实时监控**：集成测试执行状态的实时监控
- **告警机制**：添加测试失败的告警通知
- **性能分析**：添加接口响应时间分析

### 5. CI/CD 集成
- **GitHub Actions**：添加 CI/CD 配置文件
- **Docker 支持**：提供 Docker 容器化部署
- **自动化部署**：支持测试环境的自动化部署
- **版本管理**：规范化版本发布流程

### 6. 安全性增强
- **API 密钥管理**：安全的 API 密钥存储和轮换
- **访问控制**：添加基于角色的访问控制
- **审计日志**：记录所有操作的审计日志
- **数据脱敏**：对敏感数据进行脱敏处理

### 7. 扩展性改进
- **插件系统**：支持自定义插件扩展
- **多协议支持**：支持 GraphQL、gRPC 等协议
- **分布式执行**：支持跨机器的分布式测试执行
- **云原生支持**：支持 Kubernetes 等云原生环境

### 8. 用户体验优化
- **CLI 工具**：提供更友好的命令行工具
- **Web 界面**：考虑添加 Web 管理界面
- **实时反馈**：提供测试执行的实时进度反馈
- **智能推荐**：基于历史数据提供测试用例推荐

### 9. 文档完善
- **API 文档**：自动生成 API 文档
- **最佳实践**：提供测试编写的最佳实践指南
- **故障排除**：添加常见问题和解决方案
- **视频教程**：制作使用教程视频

### 10. 依赖管理
- **依赖更新**：定期更新依赖包版本
- **安全扫描**：添加依赖包的安全漏洞扫描
- **轻量化**：减少不必要的依赖，优化启动时间
- **兼容性测试**：确保在不同 Python 版本下的兼容性

## 通用化改造完成

### 🎉 框架已完成通用化改造！

本框架现已从特定业务的测试框架升级为**通用的API测试框架**，支持各种项目的接口测试需求。

### 🚀 新增核心功能

#### 1. 通用API基类
- **多种认证方式**：Bearer Token、Basic Auth、API Key、自定义认证
- **多协议支持**：REST API、GraphQL、gRPC（可扩展）
- **灵活配置**：支持多服务、多环境配置

#### 2. 插件系统
- **可扩展架构**：支持自定义插件开发
- **内置插件**：认证、数据源、验证器、报告器等
- **钩子机制**：请求前后、测试前后等多个钩子点

#### 3. 智能配置管理
- **环境变量覆盖**：支持通过环境变量动态配置
- **多格式支持**：YAML、JSON、环境变量
- **配置验证**：自动验证配置完整性

#### 4. 强大的断言系统
- **多种验证规则**：等于、包含、正则、长度等
- **JSONPath支持**：灵活的JSON数据提取
- **自定义验证器**：支持复杂业务逻辑验证

#### 5. 测试数据管理
- **多数据源**：YAML、Excel、JSON、数据库
- **数据生成**：Faker集成，自动生成测试数据
- **数据转换**：支持数据过滤、转换、参数化

#### 6. CLI工具
- **项目初始化**：快速创建新项目
- **测试执行**：灵活的测试运行选项
- **数据生成**：命令行生成测试数据

### 📖 快速开始（新项目）

#### 1. 使用CLI创建新项目
```bash
# 创建REST API测试项目
python cli.py init my-api-test --type rest_api

# 创建GraphQL测试项目
python cli.py init my-graphql-test --type graphql

# 创建gRPC测试项目
python cli.py init my-grpc-test --type grpc
```

#### 2. 配置项目
```bash
cd my-api-test
pip install -r requirements.txt

# 编辑配置文件
vim config/env_local.yml
```

#### 3. 编写测试用例
```python
from common.base_test import RestApiTestCase
from common.assertion import ValidationRule
from api.base_api import BaseApi, AuthType

class MyApi(BaseApi):
    def __init__(self):
        super().__init__(
            service_name="my_service",
            auth_type=AuthType.BEARER
        )

    def get_data(self):
        self.method = "GET"
        self.url = self.build_url("data")
        return self.send()

class TestMyApi(RestApiTestCase):
    def test_get_data(self):
        api = MyApi()
        response = api.get_data()

        rules = [
            self.create_validation_rule("$.code", "eq", 200),
            self.create_validation_rule("$.data", "is_not_null")
        ]

        self.assert_response(response, status_code=200, json_rules=rules)
```

#### 4. 运行测试
```bash
# 使用CLI运行
python cli.py run --env local

# 或使用传统方式
python run.py --env local
```

### 🔧 适配现有项目

对于现有项目，可以逐步迁移：

#### 1. 更新API基类
```python
# 旧方式
class MyApi(BaseFactoryApi):
    pass

# 新方式
class MyApi(BaseApi):
    def __init__(self):
        super().__init__(
            service_name="my_service",
            auth_type=AuthType.BEARER
        )
```

#### 2. 使用新的测试基类
```python
# 旧方式
class TestMyApi:
    pass

# 新方式
class TestMyApi(RestApiTestCase):
    pass
```

#### 3. 使用新的断言系统
```python
# 旧方式
assert response.status_code == 200
assert response.json()['code'] == 200

# 新方式
rules = [
    self.create_validation_rule("$.code", "eq", 200)
]
self.assert_response(response, status_code=200, json_rules=rules)
```

### 🎯 支持的项目类型

#### REST API项目
- 标准的RESTful API测试
- 支持各种HTTP方法
- JSON/XML数据格式支持

#### GraphQL项目
- GraphQL查询和变更测试
- Schema验证
- 查询优化分析

#### gRPC项目
- Protocol Buffers支持
- 流式RPC测试
- 服务发现集成

#### 微服务项目
- 多服务协调测试
- 服务间依赖管理
- 分布式追踪支持

### 🔌 插件开发

#### 创建自定义插件
```python
from common.plugin_system import Plugin, PluginType

class MyCustomPlugin(Plugin):
    def get_plugin_type(self) -> PluginType:
        return PluginType.VALIDATOR

    def initialize(self, config):
        # 初始化逻辑
        pass

    def validate(self, response, rules):
        # 自定义验证逻辑
        pass

# 注册插件
plugin_manager.register_plugin(MyCustomPlugin())
```

### 📊 监控和报告

#### 性能监控
- 自动记录响应时间
- 慢请求告警
- 性能趋势分析

#### 详细报告
- Allure集成报告
- 自定义报告格式
- 邮件自动发送

### 🛠️ 最佳实践

#### 1. 项目结构
```
my-project/
├── api/                    # API封装
│   ├── base_api.py        # 基础API类
│   └── user_api.py        # 具体API实现
├── testcases/             # 测试用例
│   └── test_user.py       # 测试实现
├── config/                # 配置文件
│   └── env_local.yml      # 环境配置
├── data/                  # 测试数据
│   └── users.yml          # 数据文件
└── plugins/               # 自定义插件
    └── my_plugin.py       # 插件实现
```

#### 2. 配置管理
- 使用环境变量覆盖敏感配置
- 分环境管理配置文件
- 配置验证和默认值设置

#### 3. 测试数据
- 使用数据生成器创建测试数据
- 实现测试数据隔离
- 自动清理测试数据

#### 4. 错误处理
- 统一的异常处理机制
- 详细的错误日志记录
- 失败重试和恢复策略

### 📚 更多示例

查看 `examples/` 目录获取更多使用示例：
- `rest_api_example.py` - REST API测试示例
- `database_example.py` - 数据库测试示例
- `plugin_example.py` - 插件开发示例

### 🤝 贡献指南

欢迎贡献代码和建议！请查看 `CONTRIBUTING.md` 了解详细的贡献指南。

## 联系方式

如有问题或建议，请联系项目维护者或提交Issue。
