#!/usr/bin/env python3
"""
API测试框架命令行工具

提供项目初始化、测试执行、报告生成等功能
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.config_manager import ConfigManager
from common.test_data_manager import TestDataManager
from utils.AllureUtils import AllureUtils


class CLITool:
    """命令行工具主类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.data_manager = TestDataManager()
    
    def init_project(self, project_name: str, project_type: str = "rest_api") -> None:
        """
        初始化新项目
        
        Args:
            project_name: 项目名称
            project_type: 项目类型 (rest_api, graphql, grpc)
        """
        project_path = Path(project_name)
        
        if project_path.exists():
            print(f"Error: Directory {project_name} already exists")
            return
        
        print(f"Creating new {project_type} test project: {project_name}")
        
        # 创建项目目录结构
        self._create_project_structure(project_path, project_type)
        
        # 生成配置文件
        self._generate_config_files(project_path, project_type)
        
        # 生成示例测试用例
        self._generate_sample_tests(project_path, project_type)
        
        # 生成文档
        self._generate_project_docs(project_path, project_name, project_type)
        
        print(f"Project {project_name} created successfully!")
        print(f"Next steps:")
        print(f"  1. cd {project_name}")
        print(f"  2. pip install -r requirements.txt")
        print(f"  3. Edit config files in config/ directory")
        print(f"  4. Run tests: python -m cli run")
    
    def _create_project_structure(self, project_path: Path, project_type: str) -> None:
        """创建项目目录结构"""
        directories = [
            "api",
            "testcases",
            "common",
            "config",
            "data",
            "utils",
            "plugins",
            "report",
            "logs"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
            # 创建__init__.py文件
            (project_path / directory / "__init__.py").touch()
        
        # 复制框架文件
        framework_files = [
            "common/client.py",
            "common/config_manager.py",
            "common/auth_manager.py",
            "common/assertion.py",
            "common/test_data_manager.py",
            "common/plugin_system.py",
            "common/file_load.py",
            "common/json_util.py",
            "common/logger.py",
            "utils/AllureUtils.py",
            "cli.py",
            "requirements.txt",
            ".gitignore"
        ]
        
        for file_path in framework_files:
            src_file = project_root / file_path
            dst_file = project_path / file_path
            
            if src_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
    
    def _generate_config_files(self, project_path: Path, project_type: str) -> None:
        """生成配置文件"""
        # pytest.ini
        pytest_config = """[pytest]
addopts = -sv --alluredir ./report/data --clean-alluredir -n 2 --dist=each
testpaths = ./testcases
python_files = test_*.py
python_classes = Test*
python_functions = test_*
log_cli = true
log_format = %(asctime)s %(levelname)s [%(name)s] [%(filename)s (%(funcName)s:%(lineno)d) - %(message)s]
log_date_format = %Y-%m-%d %H:%M:%S
"""
        (project_path / "pytest.ini").write_text(pytest_config)
        
        # 环境配置模板
        env_config = {
            "common": {
                "username": ["test_user"],
                "password": ["test_password"],
                "tenant_id": ["default"]
            },
            "http": {
                "default": "https://api.example.com",
                "timeout": 30,
                "verify_ssl": False
            },
            "db": {
                "host": "localhost",
                "port": 3306,
                "user": "test_user",
                "password": "test_password",
                "database": "test_db"
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "password": "",
                "db": 0
            }
        }
        
        from common.file_load import write_yaml
        write_yaml(str(project_path / "config" / "env_local.yml"), env_config)
        
        # 邮件配置模板
        email_config = {
            "email": {
                "enabled": False,
                "sender": "test@example.com",
                "password": "your_password",
                "smtp_server": "smtp.example.com",
                "smtp_port": 465,
                "receivers": ["recipient@example.com"],
                "subject_prefix": "API Test Report"
            }
        }
        write_yaml(str(project_path / "config" / "email_config.yml"), email_config)
    
    def _generate_sample_tests(self, project_path: Path, project_type: str) -> None:
        """生成示例测试用例"""
        if project_type == "rest_api":
            self._generate_rest_api_samples(project_path)
        elif project_type == "graphql":
            self._generate_graphql_samples(project_path)
        elif project_type == "grpc":
            self._generate_grpc_samples(project_path)
    
    def _generate_rest_api_samples(self, project_path: Path) -> None:
        """生成REST API示例"""
        # 基础API类
        base_api_content = '''from common.client import RequestsClient
from common.config_manager import ConfigManager
from common.auth_manager import AuthManager


class BaseApi(RequestsClient):
    """API基类"""
    
    def __init__(self, service_name: str = "default"):
        super().__init__()
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
        
        # 设置基础URL
        http_config = self.config_manager.get_http_config()
        self.host = http_config.get(service_name, http_config.get("default", ""))
        
        # 设置默认头部
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        return f"{self.host.rstrip('/')}/{endpoint.lstrip('/')}"
'''
        (project_path / "api" / "base_api.py").write_text(base_api_content)
        
        # 示例API
        sample_api_content = '''from api.base_api import BaseApi


class UserApi(BaseApi):
    """用户API"""
    
    def __init__(self):
        super().__init__("default")
    
    def get_user_list(self, page: int = 1, size: int = 10):
        """获取用户列表"""
        self.url = self.build_url(f"users?page={page}&size={size}")
        self.method = "GET"
        return self.send()
    
    def create_user(self, user_data: dict):
        """创建用户"""
        self.url = self.build_url("users")
        self.method = "POST"
        self.json = user_data
        return self.send()
    
    def get_user_by_id(self, user_id: int):
        """根据ID获取用户"""
        self.url = self.build_url(f"users/{user_id}")
        self.method = "GET"
        return self.send()
'''
        (project_path / "api" / "user_api.py").write_text(sample_api_content)
        
        # 示例测试用例
        test_content = '''import pytest
import allure
from api.user_api import UserApi
from common.assertion import FlexibleAssertion, ValidationRule
from common.test_data_manager import TestDataManager


@allure.epic("用户管理")
@allure.feature("用户API测试")
class TestUserApi:
    
    def setup_class(self):
        """测试类初始化"""
        self.user_api = UserApi()
        self.data_manager = TestDataManager()
    
    @allure.title("获取用户列表")
    def test_get_user_list(self):
        """测试获取用户列表"""
        response = self.user_api.get_user_list(page=1, size=10)
        
        # 使用通用断言
        rules = [
            ValidationRule("$.code", "eq", 200, "响应码应为200"),
            ValidationRule("$.data", "is_not_null", None, "数据不应为空"),
            ValidationRule("$.data.list", "length_ge", 0, "用户列表长度应大于等于0")
        ]
        
        results = FlexibleAssertion.assert_response(
            response, 
            status_code=200,
            json_rules=rules
        )
        
        # 检查断言结果
        for result in results:
            assert result.success, result.message
    
    @allure.title("创建用户")
    def test_create_user(self):
        """测试创建用户"""
        # 生成测试数据
        user_data = self.data_manager.generate_test_data("user")
        
        response = self.user_api.create_user(user_data)
        
        # 验证响应
        rules = [
            ValidationRule("$.code", "eq", 200, "创建成功"),
            ValidationRule("$.data.id", "is_not_null", None, "用户ID不应为空")
        ]
        
        results = FlexibleAssertion.assert_response(
            response,
            status_code=200,
            json_rules=rules
        )
        
        for result in results:
            assert result.success, result.message
'''
        (project_path / "testcases" / "test_user_api.py").write_text(test_content)
    
    def _generate_graphql_samples(self, project_path: Path) -> None:
        """生成GraphQL示例"""
        # TODO: 实现GraphQL示例生成
        pass
    
    def _generate_grpc_samples(self, project_path: Path) -> None:
        """生成gRPC示例"""
        # TODO: 实现gRPC示例生成
        pass
    
    def _generate_project_docs(self, project_path: Path, project_name: str, project_type: str) -> None:
        """生成项目文档"""
        readme_content = f"""# {project_name}

{project_type.upper()} API 自动化测试项目

## 项目结构

```
{project_name}/
├── api/                    # API接口封装
├── testcases/             # 测试用例
├── common/                # 公共工具类
├── config/                # 配置文件
├── data/                  # 测试数据
├── utils/                 # 工具类
├── plugins/               # 插件目录
├── report/                # 测试报告
├── logs/                  # 日志文件
├── cli.py                 # 命令行工具
├── pytest.ini            # pytest配置
└── requirements.txt       # 依赖包

```

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境：
   编辑 `config/env_local.yml` 文件

3. 运行测试：
   ```bash
   python -m cli run
   ```

4. 查看报告：
   测试完成后会自动打开Allure报告

## 命令行工具

```bash
# 运行所有测试
python -m cli run

# 运行指定环境的测试
python -m cli run --env prod

# 生成测试数据
python -m cli generate-data --type user --count 10

# 查看插件列表
python -m cli plugins list
```

## 配置说明

详细配置说明请参考 `config/` 目录下的配置文件。

## 扩展开发

本框架支持插件扩展，可以在 `plugins/` 目录下开发自定义插件。
"""
        (project_path / "README.md").write_text(readme_content)
    
    def run_tests(self, env: str = "local", test_path: str = None, markers: str = None) -> None:
        """
        运行测试
        
        Args:
            env: 环境名称
            test_path: 测试路径
            markers: pytest标记
        """
        import subprocess
        
        # 加载环境配置
        self.config_manager.load_env_config(env)
        
        # 构建pytest命令
        cmd = ["python", "-m", "pytest"]
        
        if test_path:
            cmd.append(test_path)
        
        if markers:
            cmd.extend(["-m", markers])
        
        # 执行测试
        print(f"Running tests with environment: {env}")
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode == 0:
            print("Tests completed successfully")
            # 启动Allure报告
            self._start_allure_report()
        else:
            print("Tests failed")
    
    def _start_allure_report(self) -> None:
        """启动Allure报告"""
        try:
            report_dir = "report/data"
            allure_port = 56766
            local_ip = AllureUtils.get_local_ip()
            report_url = f"http://{local_ip}:{allure_port}/index.html"
            
            AllureUtils.start_allure_server(report_dir, allure_port)
            print(f"Allure report available at: {report_url}")
            
        except Exception as e:
            print(f"Failed to start Allure report: {e}")
    
    def generate_test_data(self, data_type: str, count: int = 1, output_file: str = None) -> None:
        """
        生成测试数据
        
        Args:
            data_type: 数据类型
            count: 生成数量
            output_file: 输出文件
        """
        try:
            data = self.data_manager.generate_test_data(data_type, count)
            
            if output_file:
                self.data_manager.save_test_data(data, output_file.replace('.yml', '').replace('.yaml', ''))
                print(f"Test data saved to {output_file}")
            else:
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            print(f"Error generating test data: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API Test Framework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init命令
    init_parser = subparsers.add_parser("init", help="Initialize new project")
    init_parser.add_argument("project_name", help="Project name")
    init_parser.add_argument("--type", choices=["rest_api", "graphql", "grpc"], 
                           default="rest_api", help="Project type")
    
    # run命令
    run_parser = subparsers.add_parser("run", help="Run tests")
    run_parser.add_argument("--env", default="local", help="Environment name")
    run_parser.add_argument("--path", help="Test path")
    run_parser.add_argument("--markers", help="Pytest markers")
    
    # generate-data命令
    data_parser = subparsers.add_parser("generate-data", help="Generate test data")
    data_parser.add_argument("--type", required=True, help="Data type")
    data_parser.add_argument("--count", type=int, default=1, help="Count")
    data_parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLITool()
    
    if args.command == "init":
        cli.init_project(args.project_name, args.type)
    elif args.command == "run":
        cli.run_tests(args.env, args.path, args.markers)
    elif args.command == "generate-data":
        cli.generate_test_data(args.type, args.count, args.output)


if __name__ == "__main__":
    main()
