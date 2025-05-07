import logging.handlers
from datetime import datetime

from paths_manager import project_path


class GetLogger:
    """
    目前使用这种方法，会将日志文件打印在requests.log 中，控制台中未展示出来，需要在pytest.ini文件中进行配置
    """
    # 整个框架其实只需要有一个日志对象即可，可以使用单例模式实现
    # 把logger对象的初始值设置None，以类属性
    logger = None

    @classmethod
    def get_logger(cls, worker_id='master'):  #
        if cls.logger is None:
            # 创建日志名称apiautotest,这个值是自定义的
            cls.logger = logging.getLogger('apiautotest')
            # 设置日志级别，debug/info/warning/error/critical
            cls.logger.setLevel(logging.DEBUG)  # 设置为DEBUG，意味着比他等级高的日志都会被记录

            # 获取当前日期并格式化
            current_date = datetime.now().strftime('%Y-%m-%d')

            # 定义日志的一种格式
            fmt = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s (%(funcName)s:%(lineno)d) - %(message)s]"
            fm = logging.Formatter(fmt)

            # 创建日志处理器，把日志存储到文件,会存多个，以时间去分割不同的日志文件
            tf = logging.handlers.TimedRotatingFileHandler(
                # filename=f'{project_path}/logs/requests.log', # 默认会把所有日志打印在此日志文件中
                filename=f'{project_path}/logs/requests_{worker_id}_{current_date}.log',  # 多并发使用的文件名
                when='H',  # 间隔多长时间生成新的日志文件的时间单位
                interval=1,  # 间隔时间的数量
                backupCount=3,  # 除了原始最新的日志外，保留3个备份日志文件
                encoding='utf-8'
            )
            # 将日志输出到控制台上
            logging.basicConfig(level=logging.DEBUG, format=fmt)

            # 在处理器tf中添加格式
            tf.setFormatter(fm)
            # 在日志对象中添加处理器
            cls.logger.addHandler(tf)
            pass
        return cls.logger


if __name__ == '__main__':
    logger = GetLogger.get_logger()  # 得到一个日志对象
    logger.debug('这是debug日志')
    logger.info('这是info日志')
    logger.warning('这是warning日志')
    logger.error('这是error日志')
    logger.critical('这是critical日志')
