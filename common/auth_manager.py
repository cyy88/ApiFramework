"""
通用认证管理器

提供统一的认证信息管理，支持多种认证方式
"""

import os
import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

from common.config_manager import ConfigManager


class AuthManager:
    """
    通用认证管理器
    
    支持多种认证方式：
    - Bearer Token
    - Basic Auth
    - API Key
    - Custom Auth
    """
    
    _instance = None
    _auth_cache: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config_manager = ConfigManager()
            self._initialized = True
    
    def get_auth_info(self, service_name: str, auth_type: str) -> Dict[str, Any]:
        """
        获取认证信息
        
        Args:
            service_name: 服务名称
            auth_type: 认证类型
            
        Returns:
            认证信息字典
        """
        cache_key = f"{service_name}_{auth_type}"
        
        # 检查缓存
        if cache_key in self._auth_cache:
            auth_info = self._auth_cache[cache_key]
            # 检查token是否过期
            if self._is_token_valid(auth_info):
                return auth_info
        
        # 从配置获取认证信息
        auth_info = self._load_auth_from_config(service_name, auth_type)
        
        # 如果没有有效的认证信息，尝试自动登录
        if not auth_info.get('token') and auth_type.value == 'bearer':
            auth_info = self._auto_login(service_name)
        
        # 缓存认证信息
        if auth_info:
            self._auth_cache[cache_key] = auth_info
        
        return auth_info or {}
    
    def _load_auth_from_config(self, service_name: str, auth_type: str) -> Dict[str, Any]:
        """从配置文件加载认证信息"""
        # 尝试从环境变量获取
        env_token = os.getenv(f"API_TEST_TOKEN_{service_name.upper()}")
        if env_token:
            return {"token": env_token}
        
        # 从配置文件获取
        auth_config = self.config_manager.get_config('auth', default={})
        if isinstance(auth_config, dict):
            service_auth = auth_config.get(service_name, {})
            if isinstance(service_auth, dict):
                return service_auth.copy()
        
        # 从通用配置获取（向后兼容）
        common_config = self.config_manager.get_config('common', default={})
        if isinstance(common_config, dict):
            return self._extract_auth_from_common_config(common_config, service_name)
        
        return {}
    
    def _extract_auth_from_common_config(self, common_config: Dict[str, Any], service_name: str) -> Dict[str, Any]:
        """从通用配置中提取认证信息（向后兼容）"""
        auth_info = {}
        
        # 提取用户名和密码
        usernames = common_config.get('username', [])
        passwords = common_config.get('password', [])
        tenant_ids = common_config.get('tenant_id', [])
        
        if usernames and passwords:
            auth_info['username'] = usernames[0] if isinstance(usernames, list) else usernames
            auth_info['password'] = passwords[0] if isinstance(passwords, list) else passwords
            
            if tenant_ids:
                auth_info['tenant_id'] = tenant_ids[0] if isinstance(tenant_ids, list) else tenant_ids
        
        return auth_info
    
    def _auto_login(self, service_name: str) -> Dict[str, Any]:
        """自动登录获取token"""
        auth_info = self._load_auth_from_config(service_name, 'basic')
        
        if not auth_info.get('username') or not auth_info.get('password'):
            return {}
        
        try:
            # 动态导入登录API（避免循环导入）
            login_result = self._perform_login(service_name, auth_info)
            if login_result:
                auth_info.update(login_result)
                auth_info['expires_at'] = (datetime.now() + timedelta(hours=24)).isoformat()
            
        except Exception as e:
            print(f"Auto login failed for {service_name}: {e}")
        
        return auth_info
    
    def _perform_login(self, service_name: str, auth_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行登录操作"""
        # 这里可以根据不同的服务实现不同的登录逻辑
        # 为了避免循环导入，使用动态导入
        
        if service_name == 'factory':
            return self._factory_login(auth_info)
        elif service_name == 'manager':
            return self._manager_login(auth_info)
        else:
            return self._generic_login(service_name, auth_info)
    
    def _factory_login(self, auth_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """工厂端登录"""
        try:
            from api.factory.login_apis import FactoryLoginApi
            
            login_api = FactoryLoginApi(
                username=auth_info['username'],
                password=auth_info['password'],
                tenant_id=auth_info.get('tenant_id', '')
            )
            
            response = login_api.send()
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    token = data.get('data', {}).get('accessToken', '')
                    if token:
                        return {'token': token}
            
        except Exception as e:
            print(f"Factory login error: {e}")
        
        return None
    
    def _manager_login(self, auth_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """管理端登录"""
        # 实现管理端登录逻辑
        return None
    
    def _generic_login(self, service_name: str, auth_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """通用登录"""
        # 实现通用登录逻辑
        return None
    
    def _is_token_valid(self, auth_info: Dict[str, Any]) -> bool:
        """检查token是否有效"""
        if not auth_info.get('token'):
            return False
        
        expires_at = auth_info.get('expires_at')
        if not expires_at:
            return True  # 没有过期时间，假设有效
        
        try:
            expire_time = datetime.fromisoformat(expires_at)
            return datetime.now() < expire_time
        except (ValueError, TypeError):
            return True  # 解析失败，假设有效
    
    def update_auth_info(self, service_name: str, auth_data: Dict[str, Any]) -> None:
        """
        更新认证信息
        
        Args:
            service_name: 服务名称
            auth_data: 新的认证数据
        """
        # 更新所有相关的缓存
        for cache_key in list(self._auth_cache.keys()):
            if cache_key.startswith(f"{service_name}_"):
                self._auth_cache[cache_key].update(auth_data)
    
    def clear_auth_cache(self, service_name: Optional[str] = None) -> None:
        """
        清空认证缓存
        
        Args:
            service_name: 服务名称，如果为None则清空所有缓存
        """
        if service_name:
            keys_to_remove = [key for key in self._auth_cache.keys() if key.startswith(f"{service_name}_")]
            for key in keys_to_remove:
                del self._auth_cache[key]
        else:
            self._auth_cache.clear()
    
    def set_global_token(self, service_name: str, token: str, expires_in: Optional[int] = None) -> None:
        """
        设置全局token
        
        Args:
            service_name: 服务名称
            token: token值
            expires_in: 过期时间（秒）
        """
        auth_data = {'token': token}
        
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            auth_data['expires_at'] = expires_at.isoformat()
        
        # 更新所有相关的缓存
        for auth_type in ['bearer', 'custom']:
            cache_key = f"{service_name}_{auth_type}"
            if cache_key in self._auth_cache:
                self._auth_cache[cache_key].update(auth_data)
            else:
                self._auth_cache[cache_key] = auth_data.copy()


# 全局认证管理器实例
auth_manager = AuthManager()
