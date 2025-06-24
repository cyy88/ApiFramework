"""
通用断言和验证系统

提供灵活的响应验证和断言功能，支持多种验证规则
"""

import json
import re
from typing import Any, Dict, List, Union, Optional, Callable
from enum import Enum
import jsonpath
from requests import Response

from common.json_util import extract_json


class ComparisonOperator(Enum):
    """比较操作符枚举"""
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "ge"
    LESS_THAN = "lt"
    LESS_EQUAL = "le"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX_MATCH = "regex_match"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    LENGTH_EQUAL = "length_eq"
    LENGTH_GREATER = "length_gt"
    LENGTH_LESS = "length_lt"


class ValidationRule:
    """验证规则类"""
    
    def __init__(self, 
                 field_path: str,
                 operator: Union[ComparisonOperator, str],
                 expected_value: Any = None,
                 description: str = ""):
        """
        初始化验证规则
        
        Args:
            field_path: 字段路径（支持JSONPath）
            operator: 比较操作符
            expected_value: 期望值
            description: 规则描述
        """
        self.field_path = field_path
        self.operator = ComparisonOperator(operator) if isinstance(operator, str) else operator
        self.expected_value = expected_value
        self.description = description or f"{field_path} {operator} {expected_value}"


class AssertionResult:
    """断言结果类"""
    
    def __init__(self, success: bool, message: str, actual_value: Any = None, expected_value: Any = None):
        self.success = success
        self.message = message
        self.actual_value = actual_value
        self.expected_value = expected_value
    
    def __bool__(self):
        return self.success
    
    def __str__(self):
        return self.message


class ResponseValidator:
    """响应验证器"""
    
    def __init__(self, response: Response):
        """
        初始化响应验证器
        
        Args:
            response: HTTP响应对象
        """
        self.response = response
        self.json_data = None
        self.text_data = response.text
        
        # 尝试解析JSON
        try:
            self.json_data = response.json()
        except (json.JSONDecodeError, ValueError):
            pass
    
    def validate_status_code(self, expected_code: int) -> AssertionResult:
        """
        验证状态码
        
        Args:
            expected_code: 期望的状态码
            
        Returns:
            断言结果
        """
        actual_code = self.response.status_code
        success = actual_code == expected_code
        message = f"Status code: expected {expected_code}, got {actual_code}"
        
        return AssertionResult(success, message, actual_code, expected_code)
    
    def validate_header(self, header_name: str, expected_value: str) -> AssertionResult:
        """
        验证响应头
        
        Args:
            header_name: 头部名称
            expected_value: 期望值
            
        Returns:
            断言结果
        """
        actual_value = self.response.headers.get(header_name)
        success = actual_value == expected_value
        message = f"Header {header_name}: expected '{expected_value}', got '{actual_value}'"
        
        return AssertionResult(success, message, actual_value, expected_value)
    
    def validate_json_field(self, field_path: str, expected_value: Any, 
                          operator: ComparisonOperator = ComparisonOperator.EQUAL) -> AssertionResult:
        """
        验证JSON字段
        
        Args:
            field_path: 字段路径（支持JSONPath）
            expected_value: 期望值
            operator: 比较操作符
            
        Returns:
            断言结果
        """
        if self.json_data is None:
            return AssertionResult(False, "Response is not valid JSON", None, expected_value)
        
        # 提取字段值
        actual_value = self._extract_field_value(field_path)
        
        # 执行比较
        return self._compare_values(actual_value, expected_value, operator, field_path)
    
    def validate_rules(self, rules: List[ValidationRule]) -> List[AssertionResult]:
        """
        批量验证规则
        
        Args:
            rules: 验证规则列表
            
        Returns:
            断言结果列表
        """
        results = []
        
        for rule in rules:
            if rule.field_path == "status_code":
                result = self.validate_status_code(rule.expected_value)
            elif rule.field_path.startswith("header."):
                header_name = rule.field_path[7:]  # 移除 "header." 前缀
                result = self.validate_header(header_name, rule.expected_value)
            else:
                result = self.validate_json_field(rule.field_path, rule.expected_value, rule.operator)
            
            results.append(result)
        
        return results
    
    def _extract_field_value(self, field_path: str) -> Any:
        """提取字段值"""
        try:
            # 使用JSONPath提取值
            values = extract_json(self.json_data, field_path)
            
            if values is None or (isinstance(values, list) and len(values) == 0):
                return None
            elif isinstance(values, list) and len(values) == 1:
                return values[0]
            else:
                return values
                
        except Exception as e:
            print(f"Error extracting field {field_path}: {e}")
            return None
    
    def _compare_values(self, actual: Any, expected: Any, 
                       operator: ComparisonOperator, field_path: str) -> AssertionResult:
        """比较值"""
        try:
            if operator == ComparisonOperator.EQUAL:
                success = actual == expected
            elif operator == ComparisonOperator.NOT_EQUAL:
                success = actual != expected
            elif operator == ComparisonOperator.GREATER_THAN:
                success = actual > expected
            elif operator == ComparisonOperator.GREATER_EQUAL:
                success = actual >= expected
            elif operator == ComparisonOperator.LESS_THAN:
                success = actual < expected
            elif operator == ComparisonOperator.LESS_EQUAL:
                success = actual <= expected
            elif operator == ComparisonOperator.CONTAINS:
                success = expected in str(actual)
            elif operator == ComparisonOperator.NOT_CONTAINS:
                success = expected not in str(actual)
            elif operator == ComparisonOperator.STARTS_WITH:
                success = str(actual).startswith(str(expected))
            elif operator == ComparisonOperator.ENDS_WITH:
                success = str(actual).endswith(str(expected))
            elif operator == ComparisonOperator.REGEX_MATCH:
                success = bool(re.match(str(expected), str(actual)))
            elif operator == ComparisonOperator.IN:
                success = actual in expected
            elif operator == ComparisonOperator.NOT_IN:
                success = actual not in expected
            elif operator == ComparisonOperator.IS_NULL:
                success = actual is None
            elif operator == ComparisonOperator.IS_NOT_NULL:
                success = actual is not None
            elif operator == ComparisonOperator.LENGTH_EQUAL:
                success = len(actual) == expected if hasattr(actual, '__len__') else False
            elif operator == ComparisonOperator.LENGTH_GREATER:
                success = len(actual) > expected if hasattr(actual, '__len__') else False
            elif operator == ComparisonOperator.LENGTH_LESS:
                success = len(actual) < expected if hasattr(actual, '__len__') else False
            else:
                success = False
            
            message = f"Field '{field_path}': {actual} {operator.value} {expected}"
            return AssertionResult(success, message, actual, expected)
            
        except Exception as e:
            message = f"Error comparing field '{field_path}': {e}"
            return AssertionResult(False, message, actual, expected)


class FlexibleAssertion:
    """灵活的断言类"""
    
    @staticmethod
    def assert_response(response: Response, 
                       status_code: Optional[int] = None,
                       json_rules: Optional[List[ValidationRule]] = None,
                       headers: Optional[Dict[str, str]] = None,
                       custom_validators: Optional[List[Callable]] = None) -> List[AssertionResult]:
        """
        综合响应断言
        
        Args:
            response: HTTP响应对象
            status_code: 期望的状态码
            json_rules: JSON验证规则列表
            headers: 期望的响应头
            custom_validators: 自定义验证器列表
            
        Returns:
            断言结果列表
        """
        validator = ResponseValidator(response)
        results = []
        
        # 验证状态码
        if status_code is not None:
            results.append(validator.validate_status_code(status_code))
        
        # 验证响应头
        if headers:
            for header_name, expected_value in headers.items():
                results.append(validator.validate_header(header_name, expected_value))
        
        # 验证JSON规则
        if json_rules:
            results.extend(validator.validate_rules(json_rules))
        
        # 执行自定义验证器
        if custom_validators:
            for validator_func in custom_validators:
                try:
                    result = validator_func(response)
                    if isinstance(result, AssertionResult):
                        results.append(result)
                    elif isinstance(result, bool):
                        results.append(AssertionResult(result, f"Custom validator: {result}"))
                except Exception as e:
                    results.append(AssertionResult(False, f"Custom validator error: {e}"))
        
        return results
    
    @staticmethod
    def create_rule(field_path: str, operator: str, expected_value: Any, description: str = "") -> ValidationRule:
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
