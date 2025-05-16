import allure
import pytest

from api.factory.goods.add_goods import AddGoods
from common.file_load import *
from common.json_util import update_value_to_json


@allure.epic('商品管理模块')
@allure.feature('添加商品')
class TestAddSchoolApi:
    # 方法4
    json = load_yaml_file(data_yaml)['添加商品接口']

    # @pytest.mark.flaky(reruns=2, reruns_delay=2)  # 失败重试, reruns_delay为重试间隔时间单位是秒
    @allure.title('{casename}')
    @pytest.mark.parametrize(
        "casename,new_params,except_code", json)
    def test_add_school(self, casename, new_params, except_code, aalogger_init):
        add_goods = AddGoods()
        # new_params 本身是一个字典，key是json_path，value是替换的值
        for json_path, new_value in new_params.items():
            add_goods.json = update_value_to_json(add_goods.json, json_path, new_value)
        resp = add_goods.send()
        pytest.assume(resp.json()['code'] == except_code)
        if resp.json()['code'] != except_code:
            aalogger_init.error(f'{casename}接口返回信息为：{resp.json()}')
        else:
            aalogger_init.info(f'{casename}接口返回信息为：{resp.json()}')
