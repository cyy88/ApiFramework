#!/usr/bin/env python3
"""
通用API测试框架主运行脚本

支持多环境配置、插件系统、灵活的测试执行
"""

import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.AllureUtils import AllureUtils
import pytest
from common.config_manager import ConfigManager
from common.plugin_system import plugin_manager
from plugins.builtin_plugins import (
    TokenAuthPlugin, JsonDataSourcePlugin, SchemaValidatorPlugin,
    PerformanceMonitorPlugin, RequestLoggerPlugin, DataMaskingMiddleware
)


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.setup_plugins()

    def setup_plugins(self):
        """设置内置插件"""
        try:
            # 注册内置插件
            plugin_manager.register_plugin(TokenAuthPlugin())
            plugin_manager.register_plugin(JsonDataSourcePlugin())
            plugin_manager.register_plugin(SchemaValidatorPlugin())
            plugin_manager.register_plugin(PerformanceMonitorPlugin())
            plugin_manager.register_plugin(RequestLoggerPlugin())
            plugin_manager.register_plugin(DataMaskingMiddleware())

            # 从插件目录加载外部插件
            plugin_manager.load_plugins_from_directory("plugins")

            print("Plugins loaded successfully")

        except Exception as e:
            print(f"Warning: Failed to load some plugins: {e}")

    def run_tests(self, env_name: str = "local", test_path: str = None,
                  markers: str = None, parallel: bool = True) -> int:
        """
        运行测试

        Args:
            env_name: 环境名称
            test_path: 测试路径
            markers: pytest标记
            parallel: 是否并行执行

        Returns:
            测试退出码
        """
        print(f"Starting test execution with environment: {env_name}")

        # 加载环境配置
        self.load_environment_config(env_name)

        # 构建pytest参数
        pytest_args = self.build_pytest_args(test_path, markers, parallel)

        # 执行测试
        print(f"Running pytest with args: {' '.join(pytest_args)}")
        exit_code = pytest.main(pytest_args)

        # 生成和发送报告
        if exit_code == 0:
            print("Tests completed successfully")
        else:
            print(f"Tests completed with exit code: {exit_code}")

        self.handle_test_reports(env_name)

        return exit_code

    def load_environment_config(self, env_name: str):
        """加载环境配置"""
        try:
            self.config_manager.load_env_config(env_name)
            print(f"Environment configuration '{env_name}' loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load environment config '{env_name}': {e}")
            print("Using default configuration")

    def build_pytest_args(self, test_path: str = None, markers: str = None,
                         parallel: bool = True) -> list:
        """构建pytest参数"""
        args = []

        # 添加测试路径
        if test_path:
            args.append(test_path)

        # 添加标记过滤
        if markers:
            args.extend(["-m", markers])

        # 添加并行执行参数
        if parallel:
            test_config = self.config_manager.get_config('test', default={})
            workers = test_config.get('parallel_workers', 2)
            args.extend(["-n", str(workers)])

        # 添加其他配置
        args.extend(["-v", "--tb=short"])

        return args

    def handle_test_reports(self, env_name: str):
        """处理测试报告"""
        try:
            report_dir = 'report/data'
            allure_port = 56766
            local_ip = AllureUtils.get_local_ip()
            report_url = f"http://{local_ip}:{allure_port}/index.html"

            # 启动Allure报告服务器
            print("Starting Allure report server...")
            allure_process = AllureUtils.start_allure_server(report_dir, allure_port)

            # 等待服务器启动
            time.sleep(3)

            # 生成备份压缩包
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f'report/test_report_{env_name}_{timestamp}.zip'
            AllureUtils.zip_report_folder(report_dir, zip_filename)
            print(f"Report backup created: {zip_filename}")

            # 发送邮件报告
            self.send_email_report(report_url, zip_filename)

            print(f"Allure report available at: {report_url}")

            # 询问是否保持服务器运行
            try:
                keep_running = input("Keep Allure server running? (y/N): ").lower().strip()
                if keep_running in ['y', 'yes']:
                    print("Allure server will keep running. Press Ctrl+C to stop.")
                    AllureUtils.keep_server_running()
                else:
                    print("Stopping Allure server...")
            except KeyboardInterrupt:
                print("\nStopping Allure server...")

        except Exception as e:
            print(f"Error handling test reports: {e}")

    def send_email_report(self, report_url: str, zip_filename: str):
        """发送邮件报告"""
        try:
            email_config = self.config_manager.get_email_config().get('email', {})

            if email_config.get('enabled', False):
                AllureUtils.send_report_by_email(
                    email_config, report_url, 'report/data', zip_filename
                )
                print("Email report sent successfully")
            else:
                print("Email reporting is disabled")

        except Exception as e:
            print(f"Failed to send email report: {e}")

    def cleanup(self):
        """清理资源"""
        try:
            plugin_manager.cleanup_all()
        except Exception as e:
            print(f"Error during cleanup: {e}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Universal API Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Run with default environment (local)
  python run.py --env prod               # Run with production environment
  python run.py --env test --path testcases/user/  # Run specific test path
  python run.py --markers smoke         # Run tests with smoke marker
  python run.py --no-parallel           # Run tests sequentially
        """
    )

    parser.add_argument(
        '--env', '-e',
        default='local',
        help='Environment name (default: local)'
    )

    parser.add_argument(
        '--path', '-p',
        help='Test path to run (default: all tests)'
    )

    parser.add_argument(
        '--markers', '-m',
        help='Pytest markers to filter tests'
    )

    parser.add_argument(
        '--no-parallel',
        action='store_true',
        help='Disable parallel test execution'
    )

    parser.add_argument(
        '--list-plugins',
        action='store_true',
        help='List all available plugins'
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 兼容旧的命令行参数格式
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        # 旧格式: python run.py env_name
        env_name = sys.argv[1]
        sys.argv = [sys.argv[0], '--env', env_name]

    args = parse_arguments()

    runner = TestRunner()

    try:
        if args.list_plugins:
            # 列出所有插件
            plugins = plugin_manager.list_plugins()
            print("Available plugins:")
            for name, info in plugins.items():
                status = "enabled" if info['enabled'] else "disabled"
                print(f"  {name} v{info['version']} ({info['type']}) - {status}")
            return 0

        # 运行测试
        exit_code = runner.run_tests(
            env_name=args.env,
            test_path=args.path,
            markers=args.markers,
            parallel=not args.no_parallel
        )

        return exit_code

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return 1
    except Exception as e:
        print(f"Error during test execution: {e}")
        return 1
    finally:
        runner.cleanup()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
