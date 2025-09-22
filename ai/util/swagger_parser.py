import json
import time

import yaml
import copy
import os


class SwaggerParser:
    """Swagger文档解析类，用于解析Swagger/OpenAPI文档并提取API信息"""

    def __init__(self):
        """初始化SwaggerParser类"""
        pass

    def parse_swagger_doc(self, file_path):
        """解析Swagger文档
        
        Args:
            file_path: Swagger文档文件路径
            
        Returns:
            解析后的API文档对象
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

            # 判断是JSON还是YAML格式
            content = None
            try:
                content = json.loads(file_content)
            except json.JSONDecodeError:
                try:
                    content = yaml.safe_load(file_content)
                except yaml.YAMLError:
                    raise ValueError('无效的Swagger文档格式，仅支持JSON或YAML')

            # 检查是否为有效的Swagger/OpenAPI文档
            if not content or ('swagger' not in content and 'openapi' not in content):
                raise ValueError('不是有效的Swagger/OpenAPI文档，缺少swagger或openapi字段')

            # 标准化文档结构
            self._normalize_swagger_document(content)

            # 处理引用关系
            api = self._resolve_references(content)
            return api
        except Exception as error:
            print(f'解析Swagger文档时出错: {error}')
            raise

    def _normalize_swagger_document(self, doc):
        """标准化不同版本的Swagger/OpenAPI文档结构
        
        Args:
            doc: 要标准化的文档对象
        """
        # 确保paths对象存在
        if 'paths' not in doc:
            doc['paths'] = {}

        # 确保tags数组存在
        if 'tags' not in doc:
            doc['tags'] = []

        # 对于OpenAPI 3.0，确保components存在
        if 'openapi' in doc and 'components' not in doc:
            doc['components'] = {'schemas': {}}

        # 对于Swagger 2.0，确保definitions存在
        if 'swagger' in doc and 'definitions' not in doc:
            doc['definitions'] = {}

        # 处理路径操作对象
        for path, path_item in doc['paths'].items():
            # 跳过空的路径项
            if not path_item:
                continue

            # 处理各种HTTP方法
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if method in path_item:
                    operation = path_item[method]

                    # 确保操作对象有基本属性
                    if 'responses' not in operation:
                        operation['responses'] = {}
                    if 'parameters' not in operation:
                        operation['parameters'] = []
                    if 'tags' not in operation:
                        operation['tags'] = []

                    # 为没有标签的操作添加默认标签
                    if len(operation['tags']) == 0:
                        operation['tags'].append('默认')

    def _resolve_references(self, doc):
        """手动解析$ref引用
        
        Args:
            doc: 包含引用的文档对象
            
        Returns:
            解析后的API文档对象
        """
        try:
            # 创建API文档的深拷贝，避免修改原始对象
            api = copy.deepcopy(doc)

            # 确定定义的位置（Swagger 2.0用definitions，OpenAPI 3.0用components.schemas）
            definitions = api.get('definitions', {})
            if not definitions and 'components' in api:
                definitions = api['components'].get('schemas', {})

            is_openapi3 = 'openapi' in api

            # 处理路径对象中的引用
            if 'paths' in api:
                for path, path_item in api['paths'].items():
                    if not path_item:
                        continue

                    for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                        if method not in path_item:
                            continue

                        operation = path_item[method]
                        if not operation:
                            continue

                        try:
                            # 处理参数中的引用
                            if 'parameters' in operation:
                                for i, param in enumerate(operation['parameters']):
                                    try:
                                        if param and 'schema' in param and '$ref' in param['schema']:
                                            operation['parameters'][i]['schema'] = self._resolve_ref(
                                                param['schema']['$ref'], definitions
                                            )
                                    except Exception as err:
                                        print(f'解析参数引用时出错 [{path}][{method}]: {err}')

                            # 处理请求体中的引用 (OpenAPI 3.0)
                            if is_openapi3 and 'requestBody' in operation and 'content' in operation['requestBody']:
                                for media_type, content in operation['requestBody']['content'].items():
                                    try:
                                        if content and 'schema' in content and '$ref' in content['schema']:
                                            content['schema'] = self._resolve_ref(
                                                content['schema']['$ref'], definitions
                                            )
                                    except Exception as err:
                                        print(f'解析请求体引用时出错 [{path}][{method}]: {err}')

                            # 处理响应中的引用
                            if 'responses' in operation:
                                for status, response in operation['responses'].items():
                                    try:
                                        # OpenAPI 3.0 格式
                                        if is_openapi3 and response and 'content' in response:
                                            for media_type, content in response['content'].items():
                                                if content and 'schema' in content and '$ref' in content['schema']:
                                                    content['schema'] = self._resolve_ref(
                                                        content['schema']['$ref'], definitions
                                                    )
                                        # Swagger 2.0 格式
                                        elif response and 'schema' in response and '$ref' in response['schema']:
                                            response['schema'] = self._resolve_ref(
                                                response['schema']['$ref'], definitions
                                            )
                                    except Exception as err:
                                        print(f'解析响应引用时出错 [{path}][{method}][{status}]: {err}')
                        except Exception as err:
                            print(f'解析操作引用时出错 [{path}][{method}]: {err}')

            return api
        except Exception as error:
            print(f'解析引用关系时出错: {error}')
            # 返回原始文档，避免完全失败
            return doc

    def _resolve_ref(self, ref, definitions):
        """解析$ref引用
        
        Args:
            ref: 引用路径，如"#/definitions/User"
            definitions: 定义对象
            
        Returns:
            解析后的定义对象
        """
        try:
            if not ref:
                return {}

            # 从引用路径中提取名称（例如从"#/definitions/User"中提取"User"）
            parts = ref.split('/')
            ref_name = parts[-1]

            # 获取定义
            if ref_name not in definitions:
                print(f'引用未找到: {ref}')
                return {}  # 返回空对象作为默认值

            definition = definitions[ref_name]

            # 避免递归引用导致的无限循环
            if definition.get('$recursiveRef') == ref:
                return {'type': 'object', 'description': '递归引用对象'}

            # 标记此定义已被处理，防止循环引用
            result = copy.deepcopy(definition)
            result['$recursiveRef'] = ref

            # 处理属性中的引用
            if 'properties' in result:
                for prop_name, prop in result['properties'].items():
                    if prop and '$ref' in prop:
                        # 避免自引用
                        if prop['$ref'] == ref:
                            result['properties'][prop_name] = {'type': 'object', 'description': '自引用对象'}
                        else:
                            try:
                                result['properties'][prop_name] = self._resolve_ref(prop['$ref'], definitions)
                            except Exception as err:
                                print(f'解析属性引用时出错 [{prop_name}]: {err}')
                                result['properties'][prop_name] = {'type': 'object', 'description': '引用解析失败'}

            # 处理数组项中的引用
            if 'items' in result and '$ref' in result['items']:
                try:
                    # 避免自引用
                    if result['items']['$ref'] == ref:
                        result['items'] = {'type': 'object', 'description': '自引用对象'}
                    else:
                        result['items'] = self._resolve_ref(result['items']['$ref'], definitions)
                except Exception as err:
                    print(f'解析数组项引用时出错: {err}')
                    result['items'] = {'type': 'object', 'description': '引用解析失败'}

            # 移除临时标记
            if '$recursiveRef' in result:
                del result['$recursiveRef']

            return result
        except Exception as error:
            print(f'解析引用时出错 [{ref}]: {error}')
            return {'type': 'object', 'description': '引用解析失败'}

    def extract_paths(self, api):
        """提取API路径信息
        
        Args:
            api: 解析后的API文档对象
            
        Returns:
            路径信息列表
        """
        try:
            if not api or 'paths' not in api:
                print('API文档缺少paths字段')
                return []

            paths_info = []
            is_openapi3 = 'openapi' in api

            for path, path_item in api['paths'].items():
                if not path_item:
                    continue

                for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    if method not in path_item:
                        continue

                    operation = path_item[method]
                    if not operation:
                        continue

                    # 构建标准化的路径信息对象
                    path_info = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'operationId': operation.get('operationId', ''),
                        'parameters': [],
                        'requestBody': None,
                        'responses': operation.get('responses', {}),
                        'tags': operation.get('tags', [])
                    }

                    # 处理参数
                    if 'parameters' in operation:
                        path_info['parameters'] = [
                            {
                                'name': param.get('name', ''),
                                'in': param.get('in', ''),
                                'description': param.get('description', ''),
                                'required': bool(param.get('required', False)),
                                'schema': param.get('schema', {'type': param.get('type', 'string')}),
                                'type': param.get('type') or (
                                    param.get('schema', {}).get('type', 'string') if param.get('schema') else 'string')
                            }
                            for param in operation['parameters']
                        ]

                    # 处理请求体 (OpenAPI 3.0)
                    if is_openapi3 and 'requestBody' in operation:
                        path_info['requestBody'] = operation['requestBody']

                    # 处理请求体 (Swagger 2.0)
                    if not is_openapi3 and 'parameters' in operation:
                        body_param = next((p for p in operation['parameters'] if p.get('in') == 'body'), None)
                        if body_param:
                            path_info['requestBody'] = {
                                'description': body_param.get('description', ''),
                                'required': bool(body_param.get('required', False)),
                                'content': {
                                    'application/json': {
                                        'schema': body_param.get('schema', {})
                                    }
                                }
                            }

                    paths_info.append(path_info)

            return paths_info
        except Exception as error:
            print(f'提取API路径信息时出错: {error}')
            return []

    def print_api_info(self, api):
        """打印API接口信息
        
        Args:
            api: 解析后的API文档对象
        """
        try:
            print("======== API 文档信息 ========")
            print(f"文档标题: {api.get('info', {}).get('title', '未知')}")
            print(f"版本: {api.get('info', {}).get('version', '未知')}")
            print(f"描述: {api.get('info', {}).get('description', '无描述')}")
            print("\n======== API 接口列表 ========")

            # 提取路径信息
            paths_info = self.extract_paths(api)
            if not paths_info:
                print("没有找到API接口信息")
                return

            # 按标签分组显示
            tag_groups = {}
            processed_operations = set()  # 用于跟踪已处理的操作，避免重复

            for path_info in paths_info:
                # 创建操作的唯一标识符
                operation_id = f"{path_info['method']}:{path_info['path']}:{path_info.get('operationId', '')}"            
                # 如果已经处理过这个操作，则跳过
                if operation_id in processed_operations:
                    continue
                
                processed_operations.add(operation_id)
                
                # 只使用第一个标签分组（避免重复显示）
                if path_info['tags']:
                    tag = path_info['tags'][0]
                    if tag not in tag_groups:
                        tag_groups[tag] = []
                    tag_groups[tag].append(path_info)

            # 获取定义
            definitions = api.get('definitions', {})
            if not definitions and 'components' in api:
                definitions = api['components'].get('schemas', {})

            # 打印分组后的接口信息
            for tag, paths in tag_groups.items():
                print(f"\n=== {tag} ===\n")
                for path_info in paths:
                    print(f"{path_info['method']} {path_info['path']}")
                    if path_info['summary']:
                        print(f"摘要: {path_info['summary']}")
                    if path_info['description']:
                        print(f"描述: {path_info['description']}")
                    if path_info.get('operationId'):
                        print(f"操作ID: {path_info['operationId']}")

                    # 打印参数信息
                    if path_info['parameters']:
                        print("\n参数:")
                        for param in path_info['parameters']:
                            required = "必填" if param['required'] else "可选"
                            param_type = param.get('type', param.get('schema', {}).get('type', '未知'))
                            param_desc = param.get('description', '无描述')
                            
                            print(f"  - {param['name']} ({param['in']}, {required}, 类型: {param_type}): {param_desc}")
                            
                            # 如果参数有示例值，显示它
                            if 'x-example' in param:
                                print(f"    示例值: {param['x-example']}")
                            
                            # 如果是对象类型参数，展示其结构
                            if param.get('in') == 'body' and 'schema' in param and param['schema']:
                                schema = param['schema']
                                if '$ref' in schema:
                                    ref_name = schema['$ref'].split('/')[-1]
                                    if ref_name in definitions:
                                        print(f"    结构: {ref_name}")
                                        self._print_schema_structure(definitions[ref_name], '    ')

                    # 打印请求体信息
                    if path_info['requestBody']:
                        print("\n请求体:")
                        required = "必填" if path_info['requestBody'].get('required', False) else "可选"
                        print(f"  描述: {path_info['requestBody'].get('description', '无描述')} ({required})")

                        # 打印请求体结构
                        if 'content' in path_info['requestBody']:
                            for media_type, content in path_info['requestBody']['content'].items():
                                print(f"  内容类型: {media_type}")
                                if 'schema' in content:
                                    schema = content['schema']
                                    if schema:
                                        if '$ref' in schema:
                                            ref_name = schema['$ref'].split('/')[-1]
                                            if ref_name in definitions:
                                                print(f"  结构: {ref_name}")
                                                self._print_schema_structure(definitions[ref_name], '  ')
                                        else:
                                            self._print_schema_structure(schema, '  ')
                                        
                                        # 生成请求体示例
                                        example = self._generate_example(schema, definitions)
                                        if example:
                                            print("  请求示例:")
                                            formatted_example = json.dumps(example, ensure_ascii=False,
                                                                           indent=2).replace('\n', '\n    ')
                                            print(f"    {formatted_example}")

                    # 打印响应信息
                    if path_info['responses']:
                        print("\n响应:")
                        for status, response in path_info['responses'].items():
                            print(f"  - {status}: {response.get('description', '无描述')}")
                            
                            # 打印响应结构
                            if 'schema' in response:
                                schema = response['schema']
                                if schema:
                                    if '$ref' in schema:
                                        ref_name = schema['$ref'].split('/')[-1]
                                        if ref_name in definitions:
                                            print(f"    响应结构: {ref_name}")
                                            self._print_schema_structure(definitions[ref_name], '    ')
                                    else:
                                        self._print_schema_structure(schema, '    ')
                                    
                                    # 生成响应示例
                                    example = self._generate_example(schema, definitions)
                                    if example:
                                        print("    响应示例:")
                                        formatted_example = json.dumps(example, ensure_ascii=False,
                                                                           indent=2).replace('\n', '\n    ')
                                        print(f"      {formatted_example}")
                            # OpenAPI 3.0 格式
                            elif 'content' in response:
                                for media_type, content in response['content'].items():
                                    print(f"    内容类型: {media_type}")
                                    if 'schema' in content:
                                        schema = content['schema']
                                        if schema:
                                            if '$ref' in schema:
                                                ref_name = schema['$ref'].split('/')[-1]
                                                if ref_name in definitions:
                                                    print(f"    响应结构: {ref_name}")
                                                    self._print_schema_structure(definitions[ref_name], '    ')
                                            else:
                                                self._print_schema_structure(schema, '    ')
                                            
                                            # 生成响应示例
                                            example = self._generate_example(schema, definitions)
                                            if example:
                                                print("    响应示例:")
                                                formatted_example = json.dumps(example, ensure_ascii=False,
                                                                                   indent=2).replace('\n', '\n      ')\
                                                                                       .replace('\n', '\n      ')
                                                print(f"      {formatted_example}")

                    print("----------------------------")
        except Exception as error:
            print(f"打印API信息时出错: {error}")
            import traceback
            traceback.print_exc()

    def _print_schema_structure(self, schema, indent=''):
        """打印模式结构
        
        Args:
            schema: 模式对象
            indent: 缩进
        """
        try:
            if not schema:
                return
            
            schema_type = schema.get('type', 'object')
            required_props = schema.get('required', [])
            
            # 处理对象类型
            if schema_type == 'object' and 'properties' in schema:
                properties = schema.get('properties', {})
                for prop_name, prop in properties.items():
                    prop_type = prop.get('type', 'object')
                    required = "必填" if prop_name in required_props else "可选"
                    description = prop.get('description', '')
                    
                    # 格式化输出属性信息
                    print(f"{indent}- {prop_name} ({prop_type}, {required}): {description}")
                    
                    # 如果属性也是对象类型，递归打印其结构
                    if prop_type == 'object' and 'properties' in prop:
                        self._print_schema_structure(prop, indent + '  ')
                    # 如果属性是数组类型且有items，打印数组项的结构
                    elif prop_type == 'array' and 'items' in prop:
                        items = prop.get('items', {})
                        items_type = items.get('type', 'object')
                        print(f"{indent}  数组项类型: {items_type}")
                        if items_type == 'object' and 'properties' in items:
                            self._print_schema_structure(items, indent + '  ')
            
            # 处理数组类型
            elif schema_type == 'array' and 'items' in schema:
                items = schema.get('items', {})
                items_type = items.get('type', 'object')
                print(f"{indent}数组项类型: {items_type}")
                if items_type == 'object' and 'properties' in items:
                    self._print_schema_structure(items, indent + '  ')
        
        except Exception as error:
            print(f"{indent}打印模式结构时出错: {error}")

    def _generate_example(self, schema, definitions, processed_refs=None):
        """生成示例数据
        
        Args:
            schema: 模式对象
            definitions: 定义对象集合
            processed_refs: 已处理的引用，用于防止循环引用
            
        Returns:
            示例数据对象
        """
        try:
            if processed_refs is None:
                processed_refs = set()
                
            if not schema:
                return None
                
            # 处理引用
            if '$ref' in schema:
                ref = schema['$ref']
                if ref in processed_refs:
                    return {'$ref': ref}  # 避免循环引用
                    
                processed_refs.add(ref)
                ref_name = ref.split('/')[-1]
                
                if ref_name in definitions:
                    return self._generate_example(definitions[ref_name], definitions, processed_refs)
                return {'$ref': ref_name}
                
            schema_type = schema.get('type', 'object')
            
            # 处理对象类型
            if schema_type == 'object':
                result = {}
                properties = schema.get('properties', {})
                for prop_name, prop in properties.items():
                    # 使用例子值，如果有的话
                    if 'examples' in prop and prop['examples']:
                        result[prop_name] = prop['examples'][0]
                    elif 'example' in prop:
                        result[prop_name] = prop['example']
                    # 否则根据类型生成示例值
                    else:
                        result[prop_name] = self._generate_example(prop, definitions, processed_refs)
                return result
                
            # 处理数组类型
            elif schema_type == 'array':
                items = schema.get('items', {})
                if 'examples' in schema and schema['examples']:
                    return schema['examples'][0]
                elif 'example' in schema:
                    return schema['example']
                else:
                    item_example = self._generate_example(items, definitions, processed_refs)
                    return [item_example] if item_example is not None else []
                    
            # 处理字符串类型
            elif schema_type == 'string':
                if 'examples' in schema and schema['examples']:
                    return schema['examples'][0]
                elif 'example' in schema:
                    return schema['example']
                elif 'enum' in schema and schema['enum']:
                    return schema['enum'][0]
                elif schema.get('format') == 'date-time':
                    return "2023-01-01T00:00:00Z"
                elif schema.get('format') == 'date':
                    return "2023-01-01"
                return "string"
                
            # 处理数字类型
            elif schema_type in ['integer', 'number']:
                if 'examples' in schema and schema['examples']:
                    return schema['examples'][0]
                elif 'example' in schema:
                    return schema['example']
                elif schema.get('format') == 'int32':
                    return 0
                elif schema.get('format') == 'int64':
                    return 0
                elif schema.get('format') == 'float':
                    return 0.0
                elif schema.get('format') == 'double':
                    return 0.0
                return 0
                
            # 处理布尔类型
            elif schema_type == 'boolean':
                if 'examples' in schema and schema['examples']:
                    return schema['examples'][0]
                elif 'example' in schema:
                    return schema['example']
                return False
                
            return None
        except Exception as error:
            print(f"生成示例数据时出错: {error}")
            return None


# 示例使用
if __name__ == "__main__":
    start_time = time.time()
    print("开始时间：" + str(start_time))
    parser = SwaggerParser()
    # 使用示例，替换为实际的Swagger文档路径
    api = parser.parse_swagger_doc("../resources/商品.swagger.json")
    parser.print_api_info(api)
    # print("请提供Swagger文档路径作为参数运行")
    print("结束时间：" + str(time.time()))
    print("运行时间：" + str(time.time() - start_time))
