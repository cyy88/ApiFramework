import os
import sys
import smtplib
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

import pytest

from common.file_load import load_yaml_file, write_yaml
from paths_manager import common_yaml, http_yaml, db_yaml, redis_yaml, email_yaml


def zip_report_folder(report_dir, zip_filename):
    """将报告文件夹压缩成zip文件"""
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(report_dir))
                zipf.write(file_path, arcname)
    return zip_filename


def send_report_by_email(email_config, zip_filename):
    """发送测试报告到指定邮箱"""
    # 检查是否启用邮件发送功能
    if not email_config.get('enabled', False):
        print("邮件发送功能未启用，跳过发送")
        return

    # 从配置文件读取邮件设置
    sender_email = email_config.get('sender')
    password = email_config.get('password')
    smtp_server = email_config.get('smtp_server')
    smtp_port = email_config.get('smtp_port')
    receivers = email_config.get('receivers', [])
    subject_prefix = email_config.get('subject_prefix', '自动化测试报告')

    if not receivers:
        print("没有配置收件人邮箱，跳过发送")
        return

    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(receivers)
    msg['Subject'] = f"{subject_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # 邮件正文
    body = f"""
    <html>
      <body>
        <p>您好，</p>
        <p>附件是自动化测试报告，请查收。</p>
        <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # 添加附件
    with open(zip_filename, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_filename))
        msg.attach(attachment)

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print(f"测试报告已发送到: {', '.join(receivers)}")
    except Exception as e:
        print(f"邮件发送失败: {e}")


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
    # os.system('allure serve report/data')

    # 生成可发送的报告
    report_dir = 'report/data'
    zip_filename = f'report/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'

    # 压缩报告文件夹
    zip_report_folder(report_dir, zip_filename)

    # 读取邮件配置并发送报告
    try:
        email_config = load_yaml_file(email_yaml).get('email', {})
        # 发送报告到指定邮箱
        send_report_by_email(email_config, zip_filename)
    except Exception as e:
        print(f"读取邮件配置或发送邮件失败: {e}")
        # 如果配置文件不存在或发送失败，仍然可以本地查看报告
        os.system('allure serve report/data')

    # 终端输入
    # python run.py 测试环境名称    例如：python run.py yftest
