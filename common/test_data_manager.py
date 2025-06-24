"""
通用测试数据管理系统

提供灵活的测试数据管理，支持多种数据源和数据生成方式
"""

import os
import json
import random
import string
from typing import Any, Dict, List, Optional, Union, Generator
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

from common.file_load import load_yaml_file, read_excel
from common.random_util import cur_timestamp, gen_timestamp


class DataSource:
    """数据源基类"""
    
    def load_data(self, source_path: str, **kwargs) -> Any:
        """加载数据"""
        raise NotImplementedError


class YamlDataSource(DataSource):
    """YAML数据源"""
    
    def load_data(self, source_path: str, section: Optional[str] = None) -> Any:
        """
        从YAML文件加载数据
        
        Args:
            source_path: YAML文件路径
            section: 数据段名称
            
        Returns:
            加载的数据
        """
        data = load_yaml_file(source_path)
        if section and isinstance(data, dict):
            return data.get(section, [])
        return data


class ExcelDataSource(DataSource):
    """Excel数据源"""
    
    def load_data(self, source_path: str, sheet_name: str = None) -> List[List[Any]]:
        """
        从Excel文件加载数据
        
        Args:
            source_path: Excel文件路径
            sheet_name: 工作表名称
            
        Returns:
            加载的数据
        """
        return read_excel(source_path, sheet_name)


class JsonDataSource(DataSource):
    """JSON数据源"""
    
    def load_data(self, source_path: str, section: Optional[str] = None) -> Any:
        """
        从JSON文件加载数据
        
        Args:
            source_path: JSON文件路径
            section: 数据段名称
            
        Returns:
            加载的数据
        """
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if section and isinstance(data, dict):
            return data.get(section, [])
        return data


class DatabaseDataSource(DataSource):
    """数据库数据源"""
    
    def __init__(self, db_util):
        self.db_util = db_util
    
    def load_data(self, sql: str, **kwargs) -> List[Dict[str, Any]]:
        """
        从数据库加载数据
        
        Args:
            sql: SQL查询语句
            
        Returns:
            查询结果
        """
        return self.db_util.select_all(sql)


class DataGenerator:
    """数据生成器"""
    
    def __init__(self, locale: str = 'zh_CN'):
        self.faker = Faker(locale)
    
    def generate_user_data(self) -> Dict[str, Any]:
        """生成用户数据"""
        return {
            'username': self.faker.user_name(),
            'email': self.faker.email(),
            'phone': self.faker.phone_number(),
            'name': self.faker.name(),
            'address': self.faker.address(),
            'company': self.faker.company(),
            'job': self.faker.job()
        }
    
    def generate_product_data(self) -> Dict[str, Any]:
        """生成商品数据"""
        return {
            'name': self.faker.catch_phrase(),
            'description': self.faker.text(max_nb_chars=200),
            'price': round(random.uniform(1, 1000), 2),
            'category': random.choice(['电子产品', '服装', '食品', '图书', '家居']),
            'stock': random.randint(0, 1000),
            'sku': self.generate_sku()
        }
    
    def generate_order_data(self) -> Dict[str, Any]:
        """生成订单数据"""
        return {
            'order_id': self.generate_order_id(),
            'user_id': random.randint(1, 10000),
            'total_amount': round(random.uniform(10, 5000), 2),
            'status': random.choice(['pending', 'paid', 'shipped', 'delivered', 'cancelled']),
            'created_at': self.faker.date_time_between(start_date='-30d', end_date='now').isoformat(),
            'items': [self.generate_order_item() for _ in range(random.randint(1, 5))]
        }
    
    def generate_order_item(self) -> Dict[str, Any]:
        """生成订单项数据"""
        return {
            'product_id': random.randint(1, 1000),
            'quantity': random.randint(1, 10),
            'price': round(random.uniform(1, 500), 2)
        }
    
    def generate_sku(self) -> str:
        """生成SKU"""
        return f"SKU{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
    
    def generate_order_id(self) -> str:
        """生成订单ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"ORD{timestamp}{random_suffix}"
    
    def generate_random_string(self, length: int = 10, chars: str = None) -> str:
        """生成随机字符串"""
        if chars is None:
            chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))
    
    def generate_random_number(self, min_val: int = 1, max_val: int = 100) -> int:
        """生成随机数字"""
        return random.randint(min_val, max_val)
    
    def generate_timestamp(self, format_type: str = 'iso') -> Union[str, int]:
        """生成时间戳"""
        if format_type == 'iso':
            return datetime.now().isoformat()
        elif format_type == 'unix':
            return cur_timestamp()
        elif format_type == 'unix_ms':
            return cur_timestamp('ms')
        else:
            return datetime.now().strftime(format_type)


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_sources = {
            'yaml': YamlDataSource(),
            'yml': YamlDataSource(),
            'excel': ExcelDataSource(),
            'xlsx': ExcelDataSource(),
            'json': JsonDataSource()
        }
        self.generator = DataGenerator()
        self._data_cache = {}
    
    def load_test_data(self, source_name: str, **kwargs) -> Any:
        """
        加载测试数据
        
        Args:
            source_name: 数据源名称（文件名或数据库表名）
            **kwargs: 其他参数
            
        Returns:
            测试数据
        """
        # 检查缓存
        cache_key = f"{source_name}_{hash(str(kwargs))}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        # 尝试从文件加载
        data = self._load_from_file(source_name, **kwargs)
        
        if data is not None:
            self._data_cache[cache_key] = data
            return data
        
        # 如果文件不存在，返回空数据
        return []
    
    def _load_from_file(self, source_name: str, **kwargs) -> Optional[Any]:
        """从文件加载数据"""
        # 尝试不同的文件扩展名
        for ext in ['yml', 'yaml', 'json', 'xlsx', 'excel']:
            file_path = self.data_dir / f"{source_name}.{ext}"
            if file_path.exists():
                source = self.data_sources.get(ext)
                if source:
                    try:
                        return source.load_data(str(file_path), **kwargs)
                    except Exception as e:
                        print(f"Error loading data from {file_path}: {e}")
        
        return None
    
    def generate_test_data(self, data_type: str, count: int = 1, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        生成测试数据
        
        Args:
            data_type: 数据类型（user, product, order等）
            count: 生成数量
            **kwargs: 其他参数
            
        Returns:
            生成的测试数据
        """
        generator_method = getattr(self.generator, f'generate_{data_type}_data', None)
        
        if not generator_method:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        if count == 1:
            return generator_method(**kwargs)
        else:
            return [generator_method(**kwargs) for _ in range(count)]
    
    def create_parametrized_data(self, base_data: Dict[str, Any], variations: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        创建参数化测试数据
        
        Args:
            base_data: 基础数据
            variations: 变化参数
            
        Returns:
            参数化数据列表
        """
        import itertools
        
        # 获取所有变化组合
        keys = list(variations.keys())
        values = list(variations.values())
        combinations = list(itertools.product(*values))
        
        result = []
        for combination in combinations:
            data = base_data.copy()
            for i, key in enumerate(keys):
                data[key] = combination[i]
            result.append(data)
        
        return result
    
    def filter_data(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        过滤测试数据
        
        Args:
            data: 原始数据
            filters: 过滤条件
            
        Returns:
            过滤后的数据
        """
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
    
    def transform_data(self, data: Any, transformers: List[callable]) -> Any:
        """
        转换测试数据
        
        Args:
            data: 原始数据
            transformers: 转换器列表
            
        Returns:
            转换后的数据
        """
        result = data
        for transformer in transformers:
            result = transformer(result)
        return result
    
    def save_test_data(self, data: Any, filename: str, format_type: str = 'yaml') -> None:
        """
        保存测试数据
        
        Args:
            data: 要保存的数据
            filename: 文件名
            format_type: 文件格式
        """
        file_path = self.data_dir / f"{filename}.{format_type}"
        
        if format_type in ['yaml', 'yml']:
            from common.file_load import write_yaml
            write_yaml(str(file_path), data)
        elif format_type == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def clear_cache(self) -> None:
        """清空数据缓存"""
        self._data_cache.clear()


# 全局测试数据管理器实例
test_data_manager = TestDataManager()
