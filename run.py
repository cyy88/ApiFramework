import sys
import time
from datetime import datetime
from utils.AllureUtils import AllureUtils
import pytest
from common.file_load import load_yaml_file, write_yaml
from paths_manager import common_yaml, http_yaml, db_yaml, redis_yaml, email_yaml

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

    # 报告相关配置
    report_dir = 'report/data'
    allure_port = 56766  # 设置固定端口，避免冲突
    local_ip = AllureUtils.get_local_ip()
    report_url = f"http://{local_ip}:{allure_port}/index.html"

    # 启动Allure报告服务器
    allure_process = AllureUtils.start_allure_server(report_dir, allure_port)

    # 等待服务器启动
    time.sleep(5)

    # 生成备份压缩包
    zip_filename = f'report/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    AllureUtils.zip_report_folder(report_dir, zip_filename)

    # 读取邮件配置并发送报告链接
    try:
        email_config = load_yaml_file(email_yaml).get('email', {})
        # 发送报告到指定邮箱
        AllureUtils.send_report_by_email(email_config, report_url, report_dir)
    except Exception as e:
        print(f"读取邮件配置或发送邮件失败: {e}")

    # 保持服务器运行
    print(f"Allure报告已生成并发送，可通过以下链接查看: {report_url}")
    AllureUtils.keep_server_running()

    # 终端输入
    # python run.py 测试环境名称    例如：python run.py yftest
