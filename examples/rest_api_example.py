"""
REST API测试示例

展示如何使用通用框架进行REST API测试
"""

import pytest
import allure
from typing import Dict, Any

from common.base_test import RestApiTestCase
from common.assertion import ValidationRule
from api.base_api import BaseApi, AuthType


class UserApi(BaseApi):
    """用户API封装"""
    
    def __init__(self):
        super().__init__(
            service_name="user_service",
            auth_type=AuthType.BEARER
        )
    
    def get_users(self, page: int = 1, size: int = 10) -> Any:
        """获取用户列表"""
        self.method = "GET"
        self.url = self.build_url(f"users?page={page}&size={size}")
        return self.send()
    
    def create_user(self, user_data: Dict[str, Any]) -> Any:
        """创建用户"""
        self.method = "POST"
        self.url = self.build_url("users")
        self.json = user_data
        return self.send()
    
    def get_user_by_id(self, user_id: int) -> Any:
        """根据ID获取用户"""
        self.method = "GET"
        self.url = self.build_url(f"users/{user_id}")
        return self.send()
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Any:
        """更新用户"""
        self.method = "PUT"
        self.url = self.build_url(f"users/{user_id}")
        self.json = user_data
        return self.send()
    
    def delete_user(self, user_id: int) -> Any:
        """删除用户"""
        self.method = "DELETE"
        self.url = self.build_url(f"users/{user_id}")
        return self.send()


@allure.epic("用户管理系统")
@allure.feature("用户API")
class TestUserApi(RestApiTestCase):
    """用户API测试类"""
    
    @classmethod
    def setup_test_class(cls):
        """测试类初始化"""
        super().setup_test_class()
        cls.user_api = UserApi()
        cls.created_user_ids = []  # 记录创建的用户ID，用于清理
    
    @classmethod
    def teardown_test_class(cls):
        """测试类清理"""
        # 清理创建的测试用户
        for user_id in cls.created_user_ids:
            try:
                cls.user_api.delete_user(user_id)
            except Exception as e:
                print(f"Failed to cleanup user {user_id}: {e}")
        
        super().teardown_test_class()
    
    @allure.story("用户查询")
    @allure.title("获取用户列表")
    @allure.description("测试获取用户列表接口的基本功能")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_users_list(self):
        """测试获取用户列表"""
        
        with self.step("发送获取用户列表请求"):
            response = self.user_api.get_users(page=1, size=10)
        
        with self.step("验证响应结果"):
            rules = [
                self.create_validation_rule("$.code", "eq", 200, "响应码应为200"),
                self.create_validation_rule("$.data", "is_not_null", None, "数据不应为空"),
                self.create_validation_rule("$.data.list", "length_ge", 0, "用户列表长度应大于等于0"),
                self.create_validation_rule("$.data.total", "ge", 0, "总数应大于等于0")
            ]
            
            self.assert_response(
                response,
                status_code=200,
                json_rules=rules
            )
    
    @allure.story("用户创建")
    @allure.title("创建新用户")
    @allure.description("测试创建新用户接口")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self):
        """测试创建用户"""
        
        with self.step("准备测试数据"):
            user_data = self.generate_test_data("user")
            allure.attach(
                str(user_data),
                name="用户数据",
                attachment_type=allure.attachment_type.JSON
            )
        
        with self.step("发送创建用户请求"):
            response = self.user_api.create_user(user_data)
        
        with self.step("验证创建结果"):
            rules = [
                self.create_validation_rule("$.code", "eq", 200, "创建成功"),
                self.create_validation_rule("$.data.id", "is_not_null", None, "用户ID不应为空"),
                self.create_validation_rule("$.data.username", "eq", user_data["username"], "用户名应匹配"),
                self.create_validation_rule("$.data.email", "eq", user_data["email"], "邮箱应匹配")
            ]
            
            self.assert_response(
                response,
                status_code=200,
                json_rules=rules
            )
        
        with self.step("记录创建的用户ID用于清理"):
            if response.status_code == 200:
                user_id = response.json().get("data", {}).get("id")
                if user_id:
                    self.created_user_ids.append(user_id)
    
    @allure.story("用户查询")
    @allure.title("根据ID获取用户详情")
    @allure.description("测试根据用户ID获取用户详情")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        
        with self.step("先创建一个测试用户"):
            user_data = self.generate_test_data("user")
            create_response = self.user_api.create_user(user_data)
            
            self.assert_response(create_response, status_code=200)
            user_id = create_response.json()["data"]["id"]
            self.created_user_ids.append(user_id)
        
        with self.step("根据ID获取用户详情"):
            response = self.user_api.get_user_by_id(user_id)
        
        with self.step("验证用户详情"):
            rules = [
                self.create_validation_rule("$.code", "eq", 200, "获取成功"),
                self.create_validation_rule("$.data.id", "eq", user_id, "用户ID应匹配"),
                self.create_validation_rule("$.data.username", "eq", user_data["username"], "用户名应匹配")
            ]
            
            self.assert_response(
                response,
                status_code=200,
                json_rules=rules
            )
    
    @allure.story("用户更新")
    @allure.title("更新用户信息")
    @allure.description("测试更新用户信息接口")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_user(self):
        """测试更新用户"""
        
        with self.step("先创建一个测试用户"):
            user_data = self.generate_test_data("user")
            create_response = self.user_api.create_user(user_data)
            
            self.assert_response(create_response, status_code=200)
            user_id = create_response.json()["data"]["id"]
            self.created_user_ids.append(user_id)
        
        with self.step("准备更新数据"):
            update_data = {
                "name": "Updated Name",
                "email": "updated@example.com"
            }
        
        with self.step("发送更新请求"):
            response = self.user_api.update_user(user_id, update_data)
        
        with self.step("验证更新结果"):
            rules = [
                self.create_validation_rule("$.code", "eq", 200, "更新成功"),
                self.create_validation_rule("$.data.name", "eq", update_data["name"], "姓名应已更新"),
                self.create_validation_rule("$.data.email", "eq", update_data["email"], "邮箱应已更新")
            ]
            
            self.assert_response(
                response,
                status_code=200,
                json_rules=rules
            )
    
    @allure.story("用户删除")
    @allure.title("删除用户")
    @allure.description("测试删除用户接口")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_user(self):
        """测试删除用户"""
        
        with self.step("先创建一个测试用户"):
            user_data = self.generate_test_data("user")
            create_response = self.user_api.create_user(user_data)
            
            self.assert_response(create_response, status_code=200)
            user_id = create_response.json()["data"]["id"]
        
        with self.step("删除用户"):
            response = self.user_api.delete_user(user_id)
        
        with self.step("验证删除结果"):
            self.assert_response(response, status_code=200)
        
        with self.step("验证用户已被删除"):
            get_response = self.user_api.get_user_by_id(user_id)
            self.assert_response(get_response, status_code=404)
    
    @allure.story("异常处理")
    @allure.title("获取不存在的用户")
    @allure.description("测试获取不存在用户的异常处理")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_nonexistent_user(self):
        """测试获取不存在的用户"""
        
        with self.step("使用不存在的用户ID"):
            nonexistent_id = 999999
        
        with self.step("发送获取请求"):
            response = self.user_api.get_user_by_id(nonexistent_id)
        
        with self.step("验证错误响应"):
            rules = [
                self.create_validation_rule("$.code", "eq", 404, "应返回404错误"),
                self.create_validation_rule("$.message", "contains", "not found", "错误信息应包含'not found'")
            ]
            
            self.assert_response(
                response,
                status_code=404,
                json_rules=rules
            )
    
    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({"username": ""}, "用户名不能为空"),
        ({"email": "invalid-email"}, "邮箱格式不正确"),
        ({"username": "a"}, "用户名长度不能少于2位"),
    ])
    @allure.story("数据验证")
    @allure.title("创建用户时的数据验证")
    @allure.description("测试创建用户时各种无效数据的验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_user_validation(self, invalid_data, expected_error):
        """测试创建用户的数据验证"""
        
        with self.step("准备无效的用户数据"):
            base_data = self.generate_test_data("user")
            base_data.update(invalid_data)
            
            allure.attach(
                str(base_data),
                name="无效用户数据",
                attachment_type=allure.attachment_type.JSON
            )
        
        with self.step("发送创建请求"):
            response = self.user_api.create_user(base_data)
        
        with self.step("验证验证错误"):
            rules = [
                self.create_validation_rule("$.code", "eq", 400, "应返回400错误"),
                self.create_validation_rule("$.message", "contains", expected_error, f"错误信息应包含'{expected_error}'")
            ]
            
            self.assert_response(
                response,
                status_code=400,
                json_rules=rules
            )
