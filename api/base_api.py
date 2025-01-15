from common.client import RequestsClient


# 买家服务基类
from common.file_load import load_yaml_file
from paths_manager import http_yaml


class BaseFactoryApi(RequestsClient):
    # 这是定义的全局性的类属性，来代表买家token，默认是空
    # token提取赋值是在测试之前要完成的，最终会在自定义的fixture中完成
    factory_token = ''
    tenant_id = ''

    def __init__(self):
        super().__init__()  # 表示继承父类所有的属性
        self.host = load_yaml_file(http_yaml)['factory']
        self.headers = {
            "Authorization": f"Bearer  {BaseFactoryApi.factory_token}",
            "tenant-id": f"{BaseFactoryApi.tenant_id}",
            "Content-Type": "application/json"
        }


# 管理员服务基类
class BaseManagerApi(RequestsClient):
    # 这是定义的全局性的类属性，来代表买家token，默认是空
    # token提取赋值是在测试之前要完成的，最终会在自定义的fixture中完成
    manager_token = ''

    def __init__(self):
        super().__init__()  # 表示继承父类所有的属性
        self.host = 'http://59.36.173.55:7004'
        self.headers = {
            "Authorization": BaseManagerApi.manager_token
        }
