import os
import sys

import pytest

from common.file_load import load_yaml_file, write_yaml
from paths_manager import common_yaml, http_yaml, db_yaml, redis_yaml

if __name__ == '__main__':
    args = sys.argv  # 表示获取终端执行时传递的参数
    print(args)  # args是个列表，第一个元素是run.py文件名，第二个元素是环境名称
    env_file = 'config/env_yftest.yml'

    # 如果没有传入环境名称，则默认使用预发环境
    if len(args) > 1:
        env_name = args[1]  # 获取环境名称
        # 拼接环境文件路径
        env_file = f'config/env_{env_name}.yml'
        del args[1]  # 删除传进来的环境名称参数，否则会被当做pytest要执行的测试用例名称
    # 读取要执行的环境的配置文件，获取所有配置信息
    env_info = load_yaml_file(env_file)
    # 依次写入到各个配置文件中去
    write_yaml(common_yaml, env_info['common'])
    write_yaml(http_yaml, env_info['http'])
    write_yaml(db_yaml, env_info['db'])
    write_yaml(redis_yaml, env_info['redis'])
    # pytest.main()自动扫描当前pytest.ini中相关的配置，根据配置执行测试
    pytest.main()

    # 这个是直接打开测试报告，仅仅用于本地自己看
    os.system('allure serve report/data')

    # 终端输入
    # python run.py 测试环境名称    例如：python run.py yftest

    # 本地项目开始提交代码
