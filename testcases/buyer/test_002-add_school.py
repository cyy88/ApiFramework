import allure
import pytest

from api.factory.school.add_school import AddSchool
from common.file_load import *
from common.time_format import *


@allure.epic('学校管理模块')
@allure.feature('添加学校')
class TestAddSchoolApi:
    # 用excel进行数据封装，用于参数化读取，  下载 openpyxl
    # 测试数据用列表组合，每个子列表代表一条测试数据
    #  方法1
    # json = [
    #     ["正常数据",  "测试学校", 1, 2, "浙江省杭州市拱墅区石桥路与永华街交叉口滨江·春语蓝庭", "120.188966,30.346182", 0],
    #     ["学校名称为空",  "", 1, 2, "浙江省杭州市拱墅区石桥路与永华街交叉口滨江·春语蓝庭", "120.188966,30.346182", 400],
    #     ["学校地址为空",  "测试学校2", 1, 2, "", "120.188966,30.346182", 400],
    #     ["学校坐标为空", "测试学校3", 1, 2, "浙江省杭州市拱墅区石桥路与永华街交叉口滨江·春语蓝庭", "", 400]
    # ]

    # 方法2
    # json = read_excel("./data/add_school_data.xlsx", "添加学校测试数据")

    # 方法3
    # json = read_excel(add_school_data_xlsx, "添加学校测试数据")

    # 方法4
    json = load_yaml_file(data_yaml)['添加学校接口']

    @pytest.mark.flaky(reruns=2, reruns_delay=2)  # 失败重试, reruns_delay为重试间隔时间单位是秒
    @allure.title('{casename}')
    @pytest.mark.parametrize(
        "casename,school_name,school_type,isHaveCard,school_address,school_lonlat,except_code", json)
    def test_add_school(self, casename, school_name, school_type, isHaveCard, school_address, school_lonlat,
                        except_code,
                        aalogger_init, db_init, factory_login):
        # 获取当前时间
        time = get_current_formatted_time()

        logger = aalogger_init
        tenant_id = factory_login
        # 查询数据库
        select_school = db_init.select_all(f'select school_name FROM tcom_school where tenant_id = {tenant_id}')
        logger.info(f'数据库中已有的学校名称：{select_school}')
        resp = AddSchool(school_name=school_name, school_type=school_type, isHaveCard=isHaveCard,
                         school_address=school_address, school_lonlat=school_lonlat).send()

        # 验证数据库数据
        select_school = db_init.select_all(f'select school_name FROM tcom_school where tenant_id = {tenant_id}')
        logger.info(f'测试完成后数据库中有的学校名称：{select_school}')

        # 删除测试数据
        if resp.json()['code'] == 0:
            delete_query = f'delete from tcom_school where school_name = "{school_name}" and tenant_id = {tenant_id} and create_time >= "{time}"'
            logger.info(f'删除测试数据sql：{delete_query}')
            db_init.update(delete_query)
        pytest.assume(resp.json()['code'] == except_code)
