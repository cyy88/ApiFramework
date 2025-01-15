from datetime import datetime


def get_current_formatted_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
