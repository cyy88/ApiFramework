import requests
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

from common.logger import GetLogger
from common.plugin_system import plugin_manager, PluginHook


class RequestsClient:
    """
    增强的HTTP客户端

    支持插件系统、中间件、重试机制等功能
    """

    # 创建一个session
    session = requests.session()

    def __init__(self):
        """初始化客户端"""
        self.url: Optional[str] = None
        self.method: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.params: Optional[Dict[str, Any]] = None
        self.data: Optional[Union[str, Dict[str, Any]]] = None
        self.json: Optional[Dict[str, Any]] = None
        self.files: Optional[Dict[str, Any]] = None
        self.resp: Optional[requests.Response] = None
        self.timeout: int = 30
        self.verify_ssl: bool = False
        self.retry_count: int = 0
        self.retry_delay: float = 1.0
        self.middlewares: list = []

    def add_middleware(self, middleware_func) -> None:
        """
        添加中间件

        Args:
            middleware_func: 中间件函数
        """
        self.middlewares.append(middleware_func)

    def set_timeout(self, timeout: int) -> None:
        """
        设置超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout

    def set_retry(self, count: int, delay: float = 1.0) -> None:
        """
        设置重试参数

        Args:
            count: 重试次数
            delay: 重试延迟（秒）
        """
        self.retry_count = count
        self.retry_delay = delay

    def prepare_request(self) -> Dict[str, Any]:
        """准备请求数据"""
        request_data = {
            'method': self.method,
            'url': self.url,
            'headers': self.headers.copy() if self.headers else {},
            'params': self.params,
            'data': self.data,
            'json': self.json,
            'files': self.files,
            'timeout': self.timeout,
            'verify': self.verify_ssl
        }

        # 应用中间件
        for middleware in self.middlewares:
            try:
                request_data = middleware(request_data)
            except Exception as e:
                GetLogger.get_logger().warning(f"Middleware error: {e}")

        return request_data

    def send(self) -> requests.Response:
        """
        发送请求方法

        Returns:
            HTTP响应对象
        """
        # 执行前置钩子
        context = {
            'url': self.url,
            'method': self.method,
            'headers': self.headers,
            'params': self.params,
            'data': self.data,
            'json': self.json
        }
        plugin_manager.execute_hook(PluginHook.BEFORE_REQUEST, context)

        # 准备请求数据
        request_data = self.prepare_request()

        # 记录请求信息
        self._log_request(request_data)

        # 发送请求（带重试）
        last_exception = None
        for attempt in range(self.retry_count + 1):
            try:
                self.resp = RequestsClient.session.request(**request_data)

                # 记录响应信息
                self._log_response(self.resp)

                # 执行后置钩子
                response_context = context.copy()
                response_context.update({
                    'response': self.resp,
                    'status_code': self.resp.status_code,
                    'response_time': getattr(self.resp, 'elapsed', None)
                })
                plugin_manager.execute_hook(PluginHook.AFTER_REQUEST, response_context)

                return self.resp

            except Exception as e:
                last_exception = e
                GetLogger.get_logger().warning(f"Request attempt {attempt + 1} failed: {e}")

                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
                    GetLogger.get_logger().info(f"Retrying in {self.retry_delay} seconds...")

        # 所有重试都失败了
        error_msg = f"Request failed after {self.retry_count + 1} attempts: {last_exception}"
        GetLogger.get_logger().error(error_msg)

        # 执行错误钩子
        error_context = context.copy()
        error_context.update({'error': last_exception})
        plugin_manager.execute_hook(PluginHook.ON_ERROR, error_context)

        raise Exception(error_msg)

    def _log_request(self, request_data: Dict[str, Any]) -> None:
        """记录请求信息"""
        GetLogger.get_logger().debug('=' * 50)
        GetLogger.get_logger().debug(f'Request URL: {request_data.get("url")}')
        GetLogger.get_logger().debug(f'Request Method: {request_data.get("method")}')
        GetLogger.get_logger().debug(f'Request Headers: {request_data.get("headers")}')
        GetLogger.get_logger().debug(f'Request Params: {request_data.get("params")}')
        GetLogger.get_logger().debug(f'Request Data: {request_data.get("data")}')
        GetLogger.get_logger().debug(f'Request JSON: {request_data.get("json")}')
        GetLogger.get_logger().debug(f'Request Files: {request_data.get("files")}')

    def _log_response(self, response: requests.Response) -> None:
        """记录响应信息"""
        GetLogger.get_logger().debug(f'Response Status Code: {response.status_code}')
        GetLogger.get_logger().debug(f'Response Headers: {dict(response.headers)}')
        GetLogger.get_logger().debug(f'Response Body: {response.text}')

        # 记录响应时间
        if hasattr(response, 'elapsed'):
            GetLogger.get_logger().debug(f'Response Time: {response.elapsed.total_seconds():.3f}s')

    def get(self, url: str, **kwargs) -> requests.Response:
        """GET请求便捷方法"""
        self.method = 'GET'
        self.url = url
        self.params = kwargs.get('params')
        self.headers.update(kwargs.get('headers', {}))
        return self.send()

    def post(self, url: str, **kwargs) -> requests.Response:
        """POST请求便捷方法"""
        self.method = 'POST'
        self.url = url
        self.json = kwargs.get('json')
        self.data = kwargs.get('data')
        self.headers.update(kwargs.get('headers', {}))
        return self.send()

    def put(self, url: str, **kwargs) -> requests.Response:
        """PUT请求便捷方法"""
        self.method = 'PUT'
        self.url = url
        self.json = kwargs.get('json')
        self.data = kwargs.get('data')
        self.headers.update(kwargs.get('headers', {}))
        return self.send()

    def delete(self, url: str, **kwargs) -> requests.Response:
        """DELETE请求便捷方法"""
        self.method = 'DELETE'
        self.url = url
        self.params = kwargs.get('params')
        self.headers.update(kwargs.get('headers', {}))
        return self.send()

    def patch(self, url: str, **kwargs) -> requests.Response:
        """PATCH请求便捷方法"""
        self.method = 'PATCH'
        self.url = url
        self.json = kwargs.get('json')
        self.data = kwargs.get('data')
        self.headers.update(kwargs.get('headers', {}))
        return self.send()
