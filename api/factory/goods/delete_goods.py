from api.base_api import BaseFactoryApi


class DeleteGoods(BaseFactoryApi):
    """
    删除商品接口
    """
    def __init__(self, goods_id):
        super().__init__()
        # 对请求参数重新赋值
        self.params = {
            "id": goods_id
        }
        self.url = f'{self.host}/admin-api/tcom/product/delete'
        self.method = 'delete'

