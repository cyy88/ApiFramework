import json

import allure
import pytest
from common.json_util import extract_json

from api.factory.goods.add_goods import AddGoods
from api.factory.goods.delete_goods import DeleteGoods
from common.file_load import *
from common.json_util import update_value_to_json


@allure.epic('商品管理模块')
@allure.feature('删除商品')
class TestAddSchoolApi:
    json = load_yaml_file(data_yaml)['删除商品接口']

    @allure.title('{casename}')
    @pytest.mark.parametrize("casename,except_code", json)
    def test_add_school(self, casename, except_code, aalogger_init, db_init):
        # 获取数据库中最后一件添加的商品id
        goods_id = db_init.select_all(f'select id from jxt_saas.tcom_product order by create_time desc limit 1')
        aalogger_init.info(f'商品未提取id为：{goods_id}')
        # 转化为json数据
        # goods_id = json.dumps(goods_id)
        # aalogger_init.info(f'商品id转化json为：{goods_id}')
        # # 用jsonpath提取商品id出来
        # goods_id = extract_json(goods_id, '$.id')
        goods_id = goods_id[0]['id']
        aalogger_init.info(f'商品已提取id为：{goods_id}')
        delete_goods = DeleteGoods(str(goods_id))

        resp = delete_goods.send()
        pytest.assume(resp.json()['code'] == except_code)
        if resp.json()['code'] != except_code:
            aalogger_init.error(f'{casename}接口返回信息为：{resp.json()}')
        else:
            aalogger_init.info(f'{casename}接口返回信息为：{resp.json()}')

# docker run --name jenkins-docker --rm --detach --privileged --network jenkins --network-alias docker --env DOCKER_TLS_CERTDIR=/certs --volume jenkins-docker-certs:/certs/client --volume jenkins-data:/var/jenkins_home --publish 2376:2376 docker:dind --storage-driver overlay2
