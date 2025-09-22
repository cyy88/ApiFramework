from datetime import datetime


def get_current_formatted_time():
    """
    获取当前时间的格式化字符串
    :return: 当前时间的格式化字符串
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
