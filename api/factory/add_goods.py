from api.base_api import BaseFactoryApi


class AddGoods(BaseFactoryApi):
    """
    添加商品接口
    """
    def __init__(self):
        super().__init__()
        self.url = f'{self.host}/admin-api/tcom/product/create'
        self.method = 'post'

        # 这里传递的是json数据，所以需要使用json参数，而不是data
        self.json = {
            "productDetails": "<p>便宜</p>",
            "productDescribe": "实惠",
            "productSpecList": [
                {
                    "specPrice": 0.01,  #
                    "specStock": 3,
                    "commissionMoney": "2",
                    "originalPrice": "12",
                    "isLimit": 1,
                    "limitNum": 1,
                    "laundryNumber": 1,
                    "productSpecClassList": [
                        {
                            "classId": "1844295603706793989"
                        }
                    ]
                }
            ],
            "productName": "单件",
            "productCoverImage": "https://img.jietukj.com/product/微信图片_20241021170458.png",
            "productImg": "https://img.jietukj.com/product/微信图片_20241021170509.jpg",
            "productType": 3,
            "thaliType": "",
            "sortNo": 1,
            "virtualSaleNum": 100,
            "schoolId": "1844296309490716672"
        }
