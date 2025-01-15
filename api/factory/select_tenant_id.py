from api.base_api import BaseFactoryApi


class SelectTenantId(BaseFactoryApi):
    # 接口的基本信息，统一封装在init函数中
    def __init__(self, username):
        super().__init__()
        self.url = f'{self.host}/admin-api/system/tenant/get-id-by-name?name={username}'
        self.method = 'get'
        self.headers = {
            "Content-Type": "application/json"
        }
