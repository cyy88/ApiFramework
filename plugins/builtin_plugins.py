"""
内置插件集合

提供常用的插件实现，包括认证、数据处理、报告生成等
"""

import json
import time
from typing import Dict, Any, List
from datetime import datetime

from common.plugin_system import (
    Plugin, AuthPlugin, DataSourcePlugin, ValidatorPlugin, 
    ReporterPlugin, MiddlewarePlugin, HookPlugin,
    PluginType, PluginHook
)
from common.config_manager import ConfigManager


class TokenAuthPlugin(AuthPlugin):
    """Token认证插件"""
    
    def __init__(self):
        super().__init__("token_auth", "1.0.0")
        self.tokens = {}
        self.config_manager = ConfigManager()
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        self.auto_refresh = config.get('auto_refresh', True)
        self.refresh_threshold = config.get('refresh_threshold', 300)  # 5分钟
    
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """执行认证"""
        service_name = credentials.get('service_name', 'default')
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return {}
        
        # 模拟登录请求
        # 实际实现中应该调用真实的登录API
        token = f"token_{username}_{int(time.time())}"
        expires_at = time.time() + 3600  # 1小时后过期
        
        auth_info = {
            'token': token,
            'expires_at': expires_at,
            'username': username
        }
        
        self.tokens[service_name] = auth_info
        return auth_info
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新token"""
        # 模拟刷新token
        new_token = f"refreshed_{refresh_token}_{int(time.time())}"
        expires_at = time.time() + 3600
        
        return {
            'token': new_token,
            'expires_at': expires_at
        }
    
    def get_supported_hooks(self) -> List[PluginHook]:
        """获取支持的钩子"""
        return [PluginHook.BEFORE_REQUEST]
    
    def on_before_request(self, context: Dict[str, Any]) -> None:
        """请求前检查token是否需要刷新"""
        if not self.auto_refresh:
            return
        
        service_name = context.get('service_name', 'default')
        if service_name in self.tokens:
            token_info = self.tokens[service_name]
            expires_at = token_info.get('expires_at', 0)
            
            # 如果token即将过期，自动刷新
            if time.time() + self.refresh_threshold > expires_at:
                refresh_token = token_info.get('refresh_token')
                if refresh_token:
                    new_token_info = self.refresh_token(refresh_token)
                    self.tokens[service_name].update(new_token_info)


class JsonDataSourcePlugin(DataSourcePlugin):
    """JSON数据源插件"""
    
    def __init__(self):
        super().__init__("json_data_source", "1.0.0")
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        self.base_path = config.get('base_path', 'data')
    
    def load_data(self, source: str, **kwargs) -> Any:
        """加载JSON数据"""
        import os
        file_path = os.path.join(self.base_path, f"{source}.json")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 支持数据过滤
            filters = kwargs.get('filters', {})
            if filters and isinstance(data, list):
                filtered_data = []
                for item in data:
                    match = True
                    for key, value in filters.items():
                        if key not in item or item[key] != value:
                            match = False
                            break
                    if match:
                        filtered_data.append(item)
                return filtered_data
            
            return data
            
        except FileNotFoundError:
            print(f"Data file not found: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in file {file_path}: {e}")
            return []
    
    def save_data(self, data: Any, destination: str, **kwargs) -> None:
        """保存JSON数据"""
        import os
        file_path = os.path.join(self.base_path, f"{destination}.json")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class SchemaValidatorPlugin(ValidatorPlugin):
    """JSON Schema验证插件"""
    
    def __init__(self):
        super().__init__("schema_validator", "1.0.0")
        self.schemas = {}
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        self.schema_path = config.get('schema_path', 'schemas')
        self.load_schemas()
    
    def load_schemas(self) -> None:
        """加载JSON Schema文件"""
        import os
        import glob
        
        if not os.path.exists(self.schema_path):
            return
        
        schema_files = glob.glob(os.path.join(self.schema_path, "*.json"))
        for schema_file in schema_files:
            schema_name = os.path.basename(schema_file).replace('.json', '')
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                self.schemas[schema_name] = schema
            except Exception as e:
                print(f"Error loading schema {schema_file}: {e}")
    
    def validate(self, response: Any, rules: List[Any]) -> List[Any]:
        """执行Schema验证"""
        results = []
        
        try:
            import jsonschema
            
            for rule in rules:
                schema_name = rule.get('schema')
                if schema_name not in self.schemas:
                    results.append({
                        'success': False,
                        'message': f"Schema '{schema_name}' not found"
                    })
                    continue
                
                schema = self.schemas[schema_name]
                
                try:
                    if hasattr(response, 'json'):
                        data = response.json()
                    else:
                        data = response
                    
                    jsonschema.validate(data, schema)
                    results.append({
                        'success': True,
                        'message': f"Schema validation passed for '{schema_name}'"
                    })
                    
                except jsonschema.ValidationError as e:
                    results.append({
                        'success': False,
                        'message': f"Schema validation failed: {e.message}"
                    })
                    
        except ImportError:
            results.append({
                'success': False,
                'message': "jsonschema library not installed"
            })
        
        return results


class PerformanceMonitorPlugin(HookPlugin):
    """性能监控插件"""
    
    def __init__(self):
        super().__init__("performance_monitor", "1.0.0")
        self.metrics = []
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        self.threshold = config.get('response_time_threshold', 5.0)  # 5秒
        self.log_slow_requests = config.get('log_slow_requests', True)
    
    def get_supported_hooks(self) -> List[PluginHook]:
        """获取支持的钩子"""
        return [PluginHook.BEFORE_REQUEST, PluginHook.AFTER_REQUEST]
    
    def on_before_request(self, context: Dict[str, Any]) -> None:
        """请求前记录开始时间"""
        context['start_time'] = time.time()
    
    def on_after_request(self, context: Dict[str, Any]) -> None:
        """请求后计算响应时间"""
        start_time = context.get('start_time')
        if not start_time:
            return
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 记录性能指标
        metric = {
            'url': context.get('url'),
            'method': context.get('method'),
            'status_code': context.get('status_code'),
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.metrics.append(metric)
        
        # 记录慢请求
        if self.log_slow_requests and response_time > self.threshold:
            print(f"Slow request detected: {context.get('method')} {context.get('url')} "
                  f"took {response_time:.3f}s (threshold: {self.threshold}s)")
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """获取性能指标"""
        return self.metrics.copy()
    
    def clear_metrics(self) -> None:
        """清空性能指标"""
        self.metrics.clear()


class RequestLoggerPlugin(HookPlugin):
    """请求日志插件"""
    
    def __init__(self):
        super().__init__("request_logger", "1.0.0")
        self.log_file = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        log_path = config.get('log_path', 'logs/requests.log')
        self.log_requests = config.get('log_requests', True)
        self.log_responses = config.get('log_responses', True)
        
        if self.log_requests or self.log_responses:
            import os
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            self.log_file = open(log_path, 'a', encoding='utf-8')
    
    def get_supported_hooks(self) -> List[PluginHook]:
        """获取支持的钩子"""
        return [PluginHook.BEFORE_REQUEST, PluginHook.AFTER_REQUEST]
    
    def on_before_request(self, context: Dict[str, Any]) -> None:
        """记录请求日志"""
        if not self.log_requests or not self.log_file:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'request',
            'method': context.get('method'),
            'url': context.get('url'),
            'headers': context.get('headers'),
            'params': context.get('params'),
            'data': context.get('data'),
            'json': context.get('json')
        }
        
        self.log_file.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        self.log_file.flush()
    
    def on_after_request(self, context: Dict[str, Any]) -> None:
        """记录响应日志"""
        if not self.log_responses or not self.log_file:
            return
        
        response = context.get('response')
        if not response:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'response',
            'url': context.get('url'),
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.text[:1000] if len(response.text) > 1000 else response.text  # 限制长度
        }
        
        self.log_file.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        self.log_file.flush()
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.log_file:
            self.log_file.close()


class DataMaskingMiddleware(MiddlewarePlugin):
    """数据脱敏中间件"""
    
    def __init__(self):
        super().__init__("data_masking", "1.0.0")
        self.sensitive_fields = []
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        self.sensitive_fields = config.get('sensitive_fields', [
            'password', 'token', 'secret', 'key', 'phone', 'email', 'id_card'
        ])
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求数据，脱敏敏感信息"""
        if 'json' in request_data and request_data['json']:
            request_data['json'] = self._mask_data(request_data['json'])
        
        if 'data' in request_data and isinstance(request_data['data'], dict):
            request_data['data'] = self._mask_data(request_data['data'])
        
        return request_data
    
    def _mask_data(self, data: Any) -> Any:
        """递归脱敏数据"""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(field in key.lower() for field in self.sensitive_fields):
                    masked_data[key] = self._mask_value(value)
                else:
                    masked_data[key] = self._mask_data(value)
            return masked_data
        elif isinstance(data, list):
            return [self._mask_data(item) for item in data]
        else:
            return data
    
    def _mask_value(self, value: Any) -> str:
        """脱敏单个值"""
        if not isinstance(value, str):
            value = str(value)
        
        if len(value) <= 4:
            return '*' * len(value)
        else:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
