"""
插件系统架构

提供可扩展的插件系统，支持自定义扩展和第三方集成
"""

import os
import importlib
import inspect
from typing import Dict, List, Any, Type, Optional, Callable
from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum


class PluginType(Enum):
    """插件类型枚举"""
    AUTH = "auth"
    DATA_SOURCE = "data_source"
    VALIDATOR = "validator"
    REPORTER = "reporter"
    PROTOCOL = "protocol"
    MIDDLEWARE = "middleware"
    HOOK = "hook"


class PluginHook(Enum):
    """插件钩子枚举"""
    BEFORE_REQUEST = "before_request"
    AFTER_REQUEST = "after_request"
    BEFORE_TEST = "before_test"
    AFTER_TEST = "after_test"
    BEFORE_SUITE = "before_suite"
    AFTER_SUITE = "after_suite"
    ON_ERROR = "on_error"
    ON_SUCCESS = "on_success"


class Plugin(ABC):
    """插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化插件"""
        pass
    
    @abstractmethod
    def get_plugin_type(self) -> PluginType:
        """获取插件类型"""
        pass
    
    def get_supported_hooks(self) -> List[PluginHook]:
        """获取支持的钩子"""
        return []
    
    def execute_hook(self, hook: PluginHook, context: Dict[str, Any]) -> Any:
        """执行钩子"""
        method_name = f"on_{hook.value}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(context)
        return None
    
    def cleanup(self) -> None:
        """清理资源"""
        pass


class AuthPlugin(Plugin):
    """认证插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.AUTH
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """执行认证"""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新token"""
        pass


class DataSourcePlugin(Plugin):
    """数据源插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.DATA_SOURCE
    
    @abstractmethod
    def load_data(self, source: str, **kwargs) -> Any:
        """加载数据"""
        pass
    
    @abstractmethod
    def save_data(self, data: Any, destination: str, **kwargs) -> None:
        """保存数据"""
        pass


class ValidatorPlugin(Plugin):
    """验证器插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.VALIDATOR
    
    @abstractmethod
    def validate(self, response: Any, rules: List[Any]) -> List[Any]:
        """执行验证"""
        pass


class ReporterPlugin(Plugin):
    """报告器插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.REPORTER
    
    @abstractmethod
    def generate_report(self, test_results: List[Any], output_path: str) -> None:
        """生成报告"""
        pass


class ProtocolPlugin(Plugin):
    """协议插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.PROTOCOL
    
    @abstractmethod
    def send_request(self, request_data: Dict[str, Any]) -> Any:
        """发送请求"""
        pass
    
    @abstractmethod
    def parse_response(self, response: Any) -> Dict[str, Any]:
        """解析响应"""
        pass


class MiddlewarePlugin(Plugin):
    """中间件插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.MIDDLEWARE
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        return request_data
    
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理响应"""
        return response_data


class HookPlugin(Plugin):
    """钩子插件基类"""
    
    def get_plugin_type(self) -> PluginType:
        return PluginType.HOOK


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugins_by_type: Dict[PluginType, List[Plugin]] = {}
        self.hook_plugins: Dict[PluginHook, List[Plugin]] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, plugin: Plugin, config: Optional[Dict[str, Any]] = None) -> None:
        """
        注册插件
        
        Args:
            plugin: 插件实例
            config: 插件配置
        """
        if plugin.name in self.plugins:
            print(f"Warning: Plugin {plugin.name} already registered, replacing...")
        
        # 初始化插件
        plugin_config = config or {}
        plugin.initialize(plugin_config)
        
        # 注册插件
        self.plugins[plugin.name] = plugin
        self.plugin_configs[plugin.name] = plugin_config
        
        # 按类型分组
        plugin_type = plugin.get_plugin_type()
        if plugin_type not in self.plugins_by_type:
            self.plugins_by_type[plugin_type] = []
        self.plugins_by_type[plugin_type].append(plugin)
        
        # 注册钩子
        for hook in plugin.get_supported_hooks():
            if hook not in self.hook_plugins:
                self.hook_plugins[hook] = []
            self.hook_plugins[hook].append(plugin)
        
        print(f"Plugin {plugin.name} v{plugin.version} registered successfully")
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        注销插件
        
        Args:
            plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            print(f"Warning: Plugin {plugin_name} not found")
            return
        
        plugin = self.plugins[plugin_name]
        
        # 清理资源
        plugin.cleanup()
        
        # 从各个注册表中移除
        del self.plugins[plugin_name]
        del self.plugin_configs[plugin_name]
        
        # 从类型分组中移除
        plugin_type = plugin.get_plugin_type()
        if plugin_type in self.plugins_by_type:
            self.plugins_by_type[plugin_type] = [
                p for p in self.plugins_by_type[plugin_type] if p.name != plugin_name
            ]
        
        # 从钩子注册表中移除
        for hook, plugins in self.hook_plugins.items():
            self.hook_plugins[hook] = [p for p in plugins if p.name != plugin_name]
        
        print(f"Plugin {plugin_name} unregistered successfully")
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """
        根据类型获取插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            插件列表
        """
        return self.plugins_by_type.get(plugin_type, [])
    
    def execute_hook(self, hook: PluginHook, context: Dict[str, Any]) -> List[Any]:
        """
        执行钩子
        
        Args:
            hook: 钩子类型
            context: 上下文数据
            
        Returns:
            执行结果列表
        """
        results = []
        plugins = self.hook_plugins.get(hook, [])
        
        for plugin in plugins:
            if plugin.enabled:
                try:
                    result = plugin.execute_hook(hook, context)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Error executing hook {hook.value} in plugin {plugin.name}: {e}")
        
        return results
    
    def load_plugins_from_directory(self, plugin_dir: str) -> None:
        """
        从目录加载插件
        
        Args:
            plugin_dir: 插件目录路径
        """
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            print(f"Plugin directory {plugin_dir} not found")
            return
        
        # 添加插件目录到Python路径
        import sys
        if str(plugin_path.parent) not in sys.path:
            sys.path.insert(0, str(plugin_path.parent))
        
        # 扫描插件文件
        for py_file in plugin_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            try:
                module_name = f"{plugin_path.name}.{py_file.stem}"
                module = importlib.import_module(module_name)
                
                # 查找插件类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Plugin) and 
                        obj != Plugin and
                        not inspect.isabstract(obj)):
                        
                        # 实例化并注册插件
                        plugin_instance = obj()
                        self.register_plugin(plugin_instance)
                        
            except Exception as e:
                print(f"Error loading plugin from {py_file}: {e}")
    
    def enable_plugin(self, plugin_name: str) -> None:
        """启用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            print(f"Plugin {plugin_name} enabled")
    
    def disable_plugin(self, plugin_name: str) -> None:
        """禁用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            print(f"Plugin {plugin_name} disabled")
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """列出所有插件"""
        plugin_info = {}
        for name, plugin in self.plugins.items():
            plugin_info[name] = {
                'version': plugin.version,
                'type': plugin.get_plugin_type().value,
                'enabled': plugin.enabled,
                'hooks': [hook.value for hook in plugin.get_supported_hooks()]
            }
        return plugin_info
    
    def cleanup_all(self) -> None:
        """清理所有插件"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Error cleaning up plugin {plugin.name}: {e}")


# 全局插件管理器实例
plugin_manager = PluginManager()
