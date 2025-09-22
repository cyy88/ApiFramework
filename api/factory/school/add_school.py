from api.base_api import BaseFactoryApi


class AddSchool(BaseFactoryApi):
    def __init__(self, school_name, school_type, isHaveCard, school_address, school_lonlat):
        super().__init__()
        self.url = f'{self.host}/admin-api/tcom/school/create'
        self.method = 'post'

        # 这里传递的是json数据，所以需要使用json参数，而不是data
        self.json = {
            "schoolName": school_name,
            "schoolType": school_type,
            "isHaveCard": isHaveCard,
            "schoolAddress": school_address,
            "schoolLonLat": school_lonlat
        }
