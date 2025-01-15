import time

from faker import Faker

fake = Faker(locale='zh_CN')


def rdm_phone_number():
    """
    随机生成号码
    :return:
    """
    return fake.phone_number()


def cur_timestamp(level='s'):  # 到毫秒级的时间戳
    """
    生成毫秒级别的时间戳
    :param level:
    :return:
    """
    if level == 's':
        return int(time.time())  # 10位时间戳，精确到秒
    elif level == 'ms':
        return int(time.time() * 1000)  # 13位时间戳，精确到毫秒
    else:
        raise Exception(f'{level}不支持')


def gen_timestamp(start_date='+0d', end_date='+1d'):
    """
    生成指定范围内之间的时间戳
    :param start_date:
    :param end_date:
    :return:
    """
    date_time = fake.date_time_between(start_date=start_date, end_date=end_date)
    print(date_time)
    return int(time.mktime(date_time.timetuple()))


def cur_date():  # 2024-09-29
    """
    生成当前日期 2024-09-29
    :return:
    """
    return fake.date_between_dates()


def cur_date_time():  # 2022-09-29 10:07:33
    """
    生成当前日期时间 2024-09-29 10:07:33
    :return:
    """
    return fake.date_time_between_dates()


def rdm_date(pattern='%Y-%m-%d'):
    """
    随机生成日期
    :param pattern:
    :return:
    """
    return fake.date(pattern=pattern)


def rdm_date_time():
    """
    随机生成日期时间
    :return:
    """
    return fake.date_time()


if __name__ == '__main__':
    print(rdm_phone_number())
    print(rdm_date())
    print(rdm_date_time())
    print(cur_date())
    print(cur_timestamp())
    print(cur_date_time())
    # print(time.time())
    # print(time.time()*1000)
    print(gen_timestamp(start_date="-10d", end_date='+7d'))  # day
    print(gen_timestamp(start_date="+0d", end_date='+7d'))
    print(gen_timestamp('-7d', '-6d'))
