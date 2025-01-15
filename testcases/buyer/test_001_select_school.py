import allure
import jsonpath
import pytest

from api.factory.select_school import SelectSchool
from common.json_util import extract_json


@allure.epic("主流程测试")
@allure.feature("学校管理模块")
class TestSelectSchoolApi:
    # test_data = [
    #     ['产品id不存在', 7273737, 1, 500, '{"code":"004","message":"不合法"}'],
    #     ['num为0', 541, 0, 400, '{"code":"004","message":"购买数量必须大于0"}'],
    #     ['num为负数', 541, -1, 400, '{"code":"004","message":"购买数量必须大于0"}'],
    #     ['num超过库存', 541, 99999999, 500, '{"code":"451","message":"商品库存已不足，不能购买。"}']
    # ]
    #
    # # @pytest.mark.repeat(2)
    # @allure.title('{casename}')
    # @pytest.mark.parametrize('casename,sku_id,num,expect_status,expect_body', test_data)
    # def test_buy_now(self, casename, sku_id, num, expect_status, expect_body):
    #     # 实例化一个立即购买类的对象
    #     buy_now_api = BuyNowApi(sku_id=sku_id)
    #     # 由于BuyNowApi的init中并没有传递num，因此我们按照下面的方式把测试数据num传给该接口对象的参数
    #     buy_now_api.data['num'] = num
    #     # 接口对象已经准备好，发起接口调用
    #     resp = buy_now_api.send()
    #     print(resp.text)
    #     pytest.assume(resp.status_code == expect_status, f'期望值:{expect_status},实际值:{resp.status_code}')
    #     pytest.assume(resp.text == expect_body, f'期望值:{expect_body},实际值:{resp.text}')

    @allure.title("查询学校")
    # @pytest.mark.repeat(2)  # 重复执行2次
    def test_001_select_school(self):
        resp = SelectSchool().send()
        print(resp)
        # 方法1：使用jsonpath 获取json数据，这里没有打印日志，不知道是否提取成功
        # school_name = jsonpath.jsonpath(resp.json(), '$..schoolName')

        # 方法2：使用jsonpath 获取json数据，这里打印了日志，知道是否提取成功
        school_name = extract_json(resp.json(), '$..schoolName')
        print(f"使用jsonpath获取到的学校名称为：{school_name}")
        # 只能写在测试用例中，不能写在setup_class中
        pytest.assume(resp.status_code == 200, f"期待值为201，实际值为{resp.status_code}")
        print(resp.json())
