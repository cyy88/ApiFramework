from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum

from common.client import RequestsClient
from common.config_manager import ConfigManager
from common.auth_manager import AuthManager


class AuthType(Enum):
    """认证类型枚举"""
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    CUSTOM = "custom"


class BaseApi(RequestsClient, ABC):
    """
    通用API基类，支持多种认证方式和协议

    这个基类提供了通用的API接口封装，可以适配不同的项目和认证方式。
    子类只需要实现具体的业务逻辑即可。
    """

    def __init__(self,
                 service_name: str = "default",
                 auth_type: AuthType = AuthType.NONE,
                 config_section: str = "http",
                 **kwargs):
        """
        初始化API基类

        Args:
            service_name: 服务名称，用于从配置中获取对应的host
            auth_type: 认证类型
            config_section: 配置文件中的section名称
            **kwargs: 其他参数
        """
        super().__init__()

        self.service_name = service_name
        self.auth_type = auth_type
        self.config_section = config_section

        # 从配置管理器获取配置
        self.config_manager = ConfigManager()
        self._setup_host()
        self._setup_headers()
        self._setup_auth()

    def _setup_host(self) -> None:
        """设置主机地址"""
        try:
            http_config = self.config_manager.get_config(self.config_section)
            if isinstance(http_config, dict):
                self.host = http_config.get(self.service_name, http_config.get('default', ''))
            else:
                self.host = str(http_config) if http_config else ''
        except Exception as e:
            self.host = ''
            print(f"Warning: Failed to load host config: {e}")

    def _setup_headers(self) -> None:
        """设置默认请求头"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "API-Test-Framework/1.0"
        }

    def _setup_auth(self) -> None:
        """设置认证信息"""
        if self.auth_type == AuthType.NONE:
            return

        auth_manager = AuthManager()
        auth_info = auth_manager.get_auth_info(self.service_name, self.auth_type)

        if self.auth_type == AuthType.BEARER:
            token = auth_info.get('token', '')
            if token:
                self.headers["Authorization"] = f"Bearer {token}"

        elif self.auth_type == AuthType.BASIC:
            username = auth_info.get('username', '')
            password = auth_info.get('password', '')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                self.headers["Authorization"] = f"Basic {credentials}"

        elif self.auth_type == AuthType.API_KEY:
            api_key = auth_info.get('api_key', '')
            key_header = auth_info.get('key_header', 'X-API-Key')
            if api_key:
                self.headers[key_header] = api_key

        elif self.auth_type == AuthType.CUSTOM:
            # 自定义认证方式，由子类实现
            self._setup_custom_auth(auth_info)

        # 添加其他自定义头部
        custom_headers = auth_info.get('headers', {})
        if isinstance(custom_headers, dict):
            self.headers.update(custom_headers)

    def _setup_custom_auth(self, auth_info: Dict[str, Any]) -> None:
        """
        设置自定义认证方式，子类可以重写此方法

        Args:
            auth_info: 认证信息字典
        """
        pass

    def update_auth(self, auth_data: Dict[str, Any]) -> None:
        """
        更新认证信息

        Args:
            auth_data: 新的认证数据
        """
        auth_manager = AuthManager()
        auth_manager.update_auth_info(self.service_name, auth_data)
        self._setup_auth()

    def set_custom_headers(self, headers: Dict[str, str]) -> None:
        """
        设置自定义请求头

        Args:
            headers: 自定义请求头字典
        """
        if isinstance(headers, dict):
            self.headers.update(headers)

    def build_url(self, endpoint: str) -> str:
        """
        构建完整的URL

        Args:
            endpoint: API端点

        Returns:
            完整的URL
        """
        if endpoint.startswith(('http://', 'https://')):
            return endpoint

        base_url = self.host.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base_url}/{endpoint}"


# 为了向后兼容，保留原有的类名
class BaseFactoryApi(BaseApi):
    """工厂端API基类（向后兼容）"""

    def __init__(self, **kwargs):
        super().__init__(
            service_name="factory",
            auth_type=AuthType.BEARER,
            **kwargs
        )


class BaseManagerApi(BaseApi):
    """管理端API基类（向后兼容）"""

    def __init__(self, **kwargs):
        super().__init__(
            service_name="manager",
            auth_type=AuthType.CUSTOM,
            **kwargs
        )
