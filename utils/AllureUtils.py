import socket
import os
import smtplib
import zipfile
import subprocess
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


class AllureUtils:

    @classmethod
    def get_local_ip(cls):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @classmethod
    def start_allure_server(cls, report_dir, port=56766):
        """启动Allure报告服务器"""
        # 使用subprocess启动Allure服务器，不阻塞主进程
        cmd = f"allure serve -h 127.0.0.1-p {port} {report_dir}"
        print(f"启动Allure报告服务器: {cmd}")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    @classmethod
    def zip_report_folder(cls, report_dir, zip_filename):
        """将报告文件夹压缩成zip文件"""
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(report_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(report_dir))
                    zipf.write(file_path, arcname)
        return zip_filename

    @classmethod
    def send_report_by_email(cls, email_config, report_url, report_dir, zip_filename=None):
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

        # 邮件正文，包含Allure报告链接
        body = f"""
        <html>
        <body>
            <p>您好，</p>
            <p>自动化测试已完成，您可以通过以下链接查看测试报告：</p>
            <p><a href="{report_url}">点击查看测试报告</a></p>
            <p>注意：此链接仅在本次测试执行期间有效，需要在同一网络环境下访问。请尽快查看报告。</p>
            <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # 如果提供了压缩包，也作为附件发送
        if zip_filename and os.path.exists(zip_filename):
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

    @classmethod
    def keep_server_running(cls):
        """让脚本保持运行，不立即退出"""
        try:
            while True:
                print("Allure报告服务器正在运行，按Ctrl+C停止...")
                time.sleep(600)  # 每10分钟打印一次消息
        except KeyboardInterrupt:
            print("接收到停止信号，关闭服务器...")
