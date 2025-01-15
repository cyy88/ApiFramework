import logging
from typing import List

# fixture函数定义时需要写上装饰器@pytest.fixture
# scope: 该fixture函数的作用域，不指定时默认是function
# scope参数的值有以下几种：
# session: 一次pytest执行中，该fixture只会被执行一次
# package: 在一个包中，该fixture只会被执行一次
# module：在一个模块中，该fixture只会被执行一次
# class: 在一个类中，该fixture只会被执行一次
# function: 在一个函数或者方法中，该fixture只会被执行一次
# autouse: 表示该fixture函数是否被自动调用，默认是False
# autouse为False时，需要主动调用，他才会被执行

# 文件名是固定名称；注意一下
import pytest

from api.base_api import BaseFactoryApi
from api.factory.login_apis import FactoryLoginApi
from api.factory.select_tenant_id import SelectTenantId
from common.file_load import load_yaml_file
from common.logger import GetLogger
from mysql_basic.mysql_util import DBUtil
from paths_manager import common_yaml, db_yaml

work = None


def pytest_collection_modifyitems(config: "Config", items: List["Item"]):
    # items对象是pytest收集到的所有用例对象
    # 获取pytest.ini中的addopts值
    try:
        addopts = config.getini('addopts')
        if "--dist=each" in addopts:
            # 此时说明你要用的是多进程并发，我要得到当前的worker_id
            worker_id = config.workerinput.get('workerid')
        else:
            worker_id = None
    except:
        worker_id = None
    for item in items:
        # item就代表了一条用例
        if worker_id:
            item.originalname = item.originalname.encode('utf-8').decode("unicode-escape") + worker_id
            item._nodeid = item._nodeid.encode('utf-8').decode("unicode-escape") + worker_id
        else:
            item._nodeid = item._nodeid.encode('utf-8').decode("unicode-escape")


@pytest.fixture(scope='session', autouse=True)
# 这个函数名称是固定的，不能修改，否则pytest-xdist插件无法识别，无法生成单独的日志文件
def aalogger_init(worker_id):  # 传入的这个参数用于生成单独的日志文件，不同的worker会生成不同的日志文件，方便区分
    """
    创建日志对象，在测试报告中也会生成日志文件
    :return:
    """
    logger = GetLogger.get_logger(worker_id)
    logger.info('日志初始化成功')
    logger.info(f'日志初始化成功后产生的workid：{worker_id}')
    yield logger


@pytest.fixture(scope='session', autouse=True)
def factory_login(worker_id):
    # worker_id是pytest-xdist插件传过来的参数，表示当前worker的id，这个参数只能用在测试用例中，如果写在其他模块中，就相当于一个简单的参数
    """
    工厂登录
    :return:
    """
    resp = None
    tenant_id = None
    common_info = load_yaml_file(common_yaml)
    usernames = common_info['username']
    passwords = common_info['password']
    tenant_ids = common_info['tenant_id']
    # 没有使用多进程并发时，worker_id的值是master
    if worker_id == 'master':
        resp = FactoryLoginApi(username=usernames[0], password=passwords[0], tenant_id=tenant_ids[0]).send()
        tenant_id = tenant_ids[0]
    else:
        # 提取worker_id中的数字，作为索引，从yaml文件中提取对应的账号和密码，线程1对应gw0，线程2对应gw1
        index = int(worker_id[2:])
        resp = FactoryLoginApi(username=usernames[index], password=passwords[index], tenant_id=tenant_ids[index]).send()
        tenant_id = tenant_ids[index]

    # if worker_id == 'gw0' or worker_id == 'master':
    #     # 获取tenant_id
    #     # tenant_id = SelectTenantId(username='sanya').send().json()['data']
    #     tenant_id = '422'
    #     # 实例化买家登录的接口类对象，完成调用，提取token，赋值给BaseFactoryApi.factory_token
    #     resp = FactoryLoginApi(username='sanya', password='jt123456', tenant_id=tenant_id).send()
    # elif worker_id == 'gw1':
    #     # tenant_id = SelectTenantId(username='liyang').send().json()['data']
    #     tenant_id = '421'
    #     resp = FactoryLoginApi(username='liyang', password='jt123456', tenant_id=tenant_id).send()
    try:
        logging.info(f'买家登录{resp.json()}')
        print(resp.json())
        BaseFactoryApi.factory_token = resp.json()['data']['accessToken']
        BaseFactoryApi.tenant_id = tenant_id
        yield tenant_id
    except Exception as e:
        print(e)


@pytest.fixture(scope='session', autouse=False)
def db_init():
    """
    数据库连接
    :return:
    """
    logging.info('数据库连接初始化成功')
    mysql = load_yaml_file(db_yaml)
    db_util = DBUtil(host=mysql['host'], user=mysql['user'],
                     password=mysql['password'],
                     db=mysql['db'])
    yield db_util
    db_util.close()
