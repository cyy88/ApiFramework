"""
通用配置管理器

提供统一的配置文件管理，支持多种配置源和环境变量覆盖
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

from common.file_load import load_yaml_file


class ConfigManager:
    """
    通用配置管理器
    
    支持多种配置源：
    - YAML配置文件
    - JSON配置文件
    - 环境变量覆盖
    - 默认值设置
    """
    
    _instance = None
    _config_cache: Dict[str, Any] = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config_dir = Path("config")
            self.env_prefix = "API_TEST_"
            self._initialized = True
    
    def get_config(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置段名称（如 'http', 'db', 'redis'）
            key: 配置键名（可选）
            default: 默认值
            
        Returns:
            配置值
        """
        # 先检查缓存
        cache_key = f"{section}.{key}" if key else section
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # 尝试从环境变量获取
        env_value = self._get_from_env(section, key)
        if env_value is not None:
            self._config_cache[cache_key] = env_value
            return env_value
        
        # 从配置文件获取
        file_value = self._get_from_file(section, key, default)
        self._config_cache[cache_key] = file_value
        return file_value
    
    def _get_from_env(self, section: str, key: Optional[str] = None) -> Optional[Any]:
        """从环境变量获取配置"""
        if key:
            env_key = f"{self.env_prefix}{section.upper()}_{key.upper()}"
        else:
            env_key = f"{self.env_prefix}{section.upper()}"
        
        env_value = os.getenv(env_key)
        if env_value is None:
            return None
        
        # 尝试解析JSON格式的环境变量
        try:
            return json.loads(env_value)
        except (json.JSONDecodeError, ValueError):
            return env_value
    
    def _get_from_file(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """从配置文件获取配置"""
        config_file = self.config_dir / f"{section}.yml"
        
        if not config_file.exists():
            return default
        
        try:
            config_data = load_yaml_file(str(config_file))
            if key:
                return config_data.get(key, default) if isinstance(config_data, dict) else default
            return config_data
        except Exception as e:
            print(f"Warning: Failed to load config from {config_file}: {e}")
            return default
    
    def set_config(self, section: str, key: str, value: Any) -> None:
        """
        设置配置值（运行时）
        
        Args:
            section: 配置段名称
            key: 配置键名
            value: 配置值
        """
        cache_key = f"{section}.{key}"
        self._config_cache[cache_key] = value
    
    def clear_cache(self) -> None:
        """清空配置缓存"""
        self._config_cache.clear()
    
    def load_env_config(self, env_name: str) -> None:
        """
        加载环境配置文件
        
        Args:
            env_name: 环境名称（如 'dev', 'test', 'prod'）
        """
        env_file = self.config_dir / f"env_{env_name}.yml"
        if not env_file.exists():
            print(f"Warning: Environment config file {env_file} not found")
            return
        
        try:
            env_config = load_yaml_file(str(env_file))
            if not isinstance(env_config, dict):
                return
            
            # 将环境配置写入各个配置文件
            for section, config_data in env_config.items():
                if isinstance(config_data, dict):
                    section_file = self.config_dir / f"{section}.yml"
                    from common.file_load import write_yaml
                    write_yaml(str(section_file), config_data)
            
            # 清空缓存以重新加载
            self.clear_cache()
            
        except Exception as e:
            print(f"Error loading environment config: {e}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get_config('db', default={})
    
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return self.get_config('redis', default={})
    
    def get_http_config(self) -> Dict[str, Any]:
        """获取HTTP配置"""
        return self.get_config('http', default={})
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        return self.get_config('email_config', default={})
    
    def validate_config(self, section: str, required_keys: list) -> bool:
        """
        验证配置完整性
        
        Args:
            section: 配置段名称
            required_keys: 必需的配置键列表
            
        Returns:
            是否验证通过
        """
        config = self.get_config(section, default={})
        if not isinstance(config, dict):
            return False
        
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            print(f"Missing required config keys in {section}: {missing_keys}")
            return False
        
        return True
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        获取特定服务的配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务配置字典
        """
        # 尝试获取服务专用配置
        service_config = self.get_config(f"service_{service_name}", default={})
        if service_config:
            return service_config
        
        # 回退到通用HTTP配置
        http_config = self.get_http_config()
        if isinstance(http_config, dict) and service_name in http_config:
            return {"host": http_config[service_name]}
        
        return {}


# 全局配置管理器实例
config_manager = ConfigManager()
