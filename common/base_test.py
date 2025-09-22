"""
通用测试基类

提供统一的测试基础功能，包括数据管理、断言、报告等
"""

import pytest
import allure
from typing import Dict, Any, List, Optional, Type
from abc import ABC

from common.config_manager import ConfigManager
from common.test_data_manager import TestDataManager
from common.assertion import FlexibleAssertion, ValidationRule, ResponseValidator
from common.plugin_system import plugin_manager, PluginHook
from api.base_api import BaseApi


class BaseTestCase(ABC):
    """
    通用测试基类
    
    提供统一的测试基础功能，所有测试类都应该继承此类
    """
    
    @classmethod
    def setup_class(cls):
        """测试类级别的初始化"""
        cls.config_manager = ConfigManager()
        cls.data_manager = TestDataManager()
        cls.test_data = {}
        cls.api_clients = {}
        
        # 执行插件钩子
        context = {'test_class': cls.__name__}
        plugin_manager.execute_hook(PluginHook.BEFORE_SUITE, context)
        
        # 调用子类的初始化方法
        if hasattr(cls, 'setup_test_class'):
            cls.setup_test_class()
    
    @classmethod
    def teardown_class(cls):
        """测试类级别的清理"""
        # 清理API客户端
        for client in cls.api_clients.values():
            if hasattr(client, 'cleanup'):
                client.cleanup()
        
        # 执行插件钩子
        context = {'test_class': cls.__name__}
        plugin_manager.execute_hook(PluginHook.AFTER_SUITE, context)
        
        # 调用子类的清理方法
        if hasattr(cls, 'teardown_test_class'):
            cls.teardown_test_class()
    
    def setup_method(self, method):
        """测试方法级别的初始化"""
        self.current_test = method.__name__
        
        # 执行插件钩子
        context = {
            'test_class': self.__class__.__name__,
            'test_method': self.current_test
        }
        plugin_manager.execute_hook(PluginHook.BEFORE_TEST, context)
        
        # 调用子类的初始化方法
        if hasattr(self, 'setup_test_method'):
            self.setup_test_method(method)
    
    def teardown_method(self, method):
        """测试方法级别的清理"""
        # 执行插件钩子
        context = {
            'test_class': self.__class__.__name__,
            'test_method': self.current_test,
            'test_result': getattr(self, '_test_result', 'unknown')
        }
        plugin_manager.execute_hook(PluginHook.AFTER_TEST, context)
        
        # 调用子类的清理方法
        if hasattr(self, 'teardown_test_method'):
            self.teardown_test_method(method)
    
    def get_api_client(self, service_name: str, api_class: Type[BaseApi] = None) -> BaseApi:
        """
        获取API客户端实例
        
        Args:
            service_name: 服务名称
            api_class: API类，如果为None则使用BaseApi
            
        Returns:
            API客户端实例
        """
        if service_name not in self.api_clients:
            if api_class is None:
                api_class = BaseApi
            
            self.api_clients[service_name] = api_class(service_name=service_name)
        
        return self.api_clients[service_name]
    
    def load_test_data(self, data_source: str, **kwargs) -> Any:
        """
        加载测试数据
        
        Args:
            data_source: 数据源名称
            **kwargs: 其他参数
            
        Returns:
            测试数据
        """
        return self.data_manager.load_test_data(data_source, **kwargs)
    
    def generate_test_data(self, data_type: str, count: int = 1, **kwargs) -> Any:
        """
        生成测试数据
        
        Args:
            data_type: 数据类型
            count: 生成数量
            **kwargs: 其他参数
            
        Returns:
            生成的测试数据
        """
        return self.data_manager.generate_test_data(data_type, count, **kwargs)
    
    def assert_response(self, response, status_code: int = None, 
                       json_rules: List[ValidationRule] = None,
                       headers: Dict[str, str] = None,
                       custom_validators: List = None) -> None:
        """
        通用响应断言
        
        Args:
            response: HTTP响应对象
            status_code: 期望的状态码
            json_rules: JSON验证规则
            headers: 期望的响应头
            custom_validators: 自定义验证器
        """
        results = FlexibleAssertion.assert_response(
            response, status_code, json_rules, headers, custom_validators
        )
        
        # 检查所有断言结果
        failed_assertions = [result for result in results if not result.success]
        
        if failed_assertions:
            # 记录失败信息到Allure
            for failure in failed_assertions:
                allure.attach(
                    failure.message,
                    name="Assertion Failure",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # 抛出断言错误
            failure_messages = [f.message for f in failed_assertions]
            pytest.fail(f"Assertion failures:\n" + "\n".join(failure_messages))
        
        # 记录成功信息到Allure
        success_count = len(results) - len(failed_assertions)
        if success_count > 0:
            allure.attach(
                f"{success_count} assertions passed",
                name="Assertion Summary",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def create_validation_rule(self, field_path: str, operator: str, 
                             expected_value: Any, description: str = "") -> ValidationRule:
        """
        创建验证规则的便捷方法
        
        Args:
            field_path: 字段路径
            operator: 操作符
            expected_value: 期望值
            description: 描述
            
        Returns:
            验证规则
        """
        return ValidationRule(field_path, operator, expected_value, description)
    
    def attach_request_info(self, response, title: str = "Request/Response Info"):
        """
        将请求响应信息附加到Allure报告
        
        Args:
            response: HTTP响应对象
            title: 附件标题
        """
        if hasattr(response, 'request'):
            request = response.request
            
            # 请求信息
            request_info = f"""
Request URL: {request.url}
Request Method: {request.method}
Request Headers: {dict(request.headers)}
Request Body: {getattr(request, 'body', 'N/A')}
"""
            
            # 响应信息
            response_info = f"""
Response Status: {response.status_code}
Response Headers: {dict(response.headers)}
Response Body: {response.text}
"""
            
            allure.attach(
                request_info + "\n" + response_info,
                name=title,
                attachment_type=allure.attachment_type.TEXT
            )
    
    def step(self, title: str):
        """
        Allure步骤装饰器的便捷方法
        
        Args:
            title: 步骤标题
            
        Returns:
            Allure步骤上下文管理器
        """
        return allure.step(title)
    
    def mark_test_result(self, result: str, reason: str = ""):
        """
        标记测试结果
        
        Args:
            result: 测试结果 (passed, failed, skipped)
            reason: 原因描述
        """
        self._test_result = result
        
        if result == "failed" and reason:
            allure.attach(
                reason,
                name="Failure Reason",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def skip_test(self, reason: str):
        """
        跳过测试
        
        Args:
            reason: 跳过原因
        """
        self.mark_test_result("skipped", reason)
        pytest.skip(reason)
    
    def parametrize_from_data(self, data_source: str, **kwargs):
        """
        从数据源创建参数化装饰器
        
        Args:
            data_source: 数据源名称
            **kwargs: 其他参数
            
        Returns:
            pytest.mark.parametrize装饰器
        """
        test_data = self.load_test_data(data_source, **kwargs)
        
        if not test_data:
            return pytest.mark.skip(reason=f"No test data found in {data_source}")
        
        # 假设数据格式为 [["case_name", param1, param2, ...], ...]
        if isinstance(test_data, list) and len(test_data) > 0:
            if isinstance(test_data[0], list):
                # 提取参数名（假设第一行是参数名或者使用默认名称）
                param_names = ["case_name"] + [f"param{i}" for i in range(len(test_data[0]) - 1)]
                return pytest.mark.parametrize(",".join(param_names), test_data)
            else:
                # 单参数情况
                return pytest.mark.parametrize("test_data", test_data)
        
        return pytest.mark.skip(reason=f"Invalid test data format in {data_source}")


class RestApiTestCase(BaseTestCase):
    """REST API测试基类"""
    
    def setup_test_class(cls):
        """REST API测试类初始化"""
        # 设置默认的HTTP配置
        http_config = cls.config_manager.get_http_config()
        cls.default_timeout = http_config.get('timeout', 30)
        cls.verify_ssl = http_config.get('verify_ssl', False)
    
    def send_request(self, api_client: BaseApi, method: str, endpoint: str, **kwargs):
        """
        发送HTTP请求的便捷方法
        
        Args:
            api_client: API客户端
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应对象
        """
        api_client.method = method.upper()
        api_client.url = api_client.build_url(endpoint)
        
        # 设置请求参数
        if 'json' in kwargs:
            api_client.json = kwargs['json']
        if 'data' in kwargs:
            api_client.data = kwargs['data']
        if 'params' in kwargs:
            api_client.params = kwargs['params']
        if 'headers' in kwargs:
            api_client.set_custom_headers(kwargs['headers'])
        
        # 发送请求
        response = api_client.send()
        
        # 附加请求信息到报告
        self.attach_request_info(response)
        
        return response


class DatabaseTestCase(BaseTestCase):
    """数据库测试基类"""
    
    @classmethod
    def setup_test_class(cls):
        """数据库测试类初始化"""
        from mysql_basic.mysql_util import DBUtil
        
        db_config = cls.config_manager.get_database_config()
        if db_config:
            cls.db_util = DBUtil(**db_config)
        else:
            cls.db_util = None
    
    @classmethod
    def teardown_test_class(cls):
        """数据库测试类清理"""
        if hasattr(cls, 'db_util') and cls.db_util:
            cls.db_util.close()
    
    def execute_sql(self, sql: str, params: tuple = None):
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            params: 参数
            
        Returns:
            查询结果
        """
        if not self.db_util:
            self.skip_test("Database not configured")
        
        try:
            if sql.strip().upper().startswith('SELECT'):
                return self.db_util.select_all(sql)
            else:
                return self.db_util.update(sql)
        except Exception as e:
            allure.attach(
                f"SQL: {sql}\nError: {str(e)}",
                name="Database Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
