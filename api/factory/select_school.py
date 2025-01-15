from api.base_api import BaseFactoryApi


class SelectSchool(BaseFactoryApi):
    def __init__(self):
        super().__init__()
        self.url = f'{self.host}/admin-api/tcom/school/page?pageNo=1&pageSize=20'
        self.method = 'get'
