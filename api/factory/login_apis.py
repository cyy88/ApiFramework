from api.base_api import BaseFactoryApi


class FactoryLoginApi(BaseFactoryApi):

    # 接口的基本信息，统一封装在init函数中
    def __init__(self, username, password, tenant_id):
        super().__init__()
        self.url = f'{self.host}/admin-api/system/auth/login'
        self.method = 'post'
        self.headers = {
            "Content-Type": "application/json",
            "tenant-id": f"{tenant_id}"
        }
        self.json = {
            "username": username,
            "password": password
        }


if __name__ == '__main__':
    print('sss')
    api = FactoryLoginApi('sanya', 'jt123456').send()
    print(api.json())
