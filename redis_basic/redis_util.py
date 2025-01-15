import javaobj
import redis


class RedisUtil:

    def __init__(self, host, pwd, port=6379, decode_responses=False):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=pwd,
            decode_responses=decode_responses
        )
        self.r = redis.Redis(connection_pool=self.pool)  # 拿到一个操作对象

    # 提供统一的数据获取方法
    def get(self, key):
        # 判断目标数据的类型，来决定要使用哪个获取方法
        type = self.r.type(key)
        if type == b'string' or type == 'string':
            return self.r.get(key)
        elif type == b'hash' or type == 'hash':
            return self.r.hgetall(key)
        elif type == b'list' or type == 'list':
            return self.r.lrange(key, 0, -1)
        elif type == b'set' or type == 'set':
            return self.r.smembers(key)
        elif type == b'zset' or type == 'zset':
            return self.r.zrange(key, 0, -1)
        else:
            raise BaseException(f'{key}的数据类型不支持')


if __name__ == '__main__':

    # decode_responses表示是否针对结果去做decode转码
    # pool = redis.ConnectionPool(
    #     host='82.156.77.202',
    #     port=6389,
    #     password='mtx',
    #     decode_responses=False
    # )
    # r = redis.Redis(connection_pool=pool)  # 拿到一个操作对象
    r = RedisUtil(host='82.156.74.26', port=6379, pwd='mtx')

    # 解析订单参数缓存数据(收货地址、付款方式、送货时间、备注、...)
    res = r.get('{CHECKOUT_PARAM_ID_PREFIX}_59')
    # 这个缓存数据在redis中是hash类型，那么读出来以后结果就是python中的字典
    print(type(res))
    print(res)
    # 这个字典里的key/value通通都是java中的数据，因此我们要遍历字典
    # 将字典的key/value的java数据转成python数据
    for key, value in res.items():
        key = javaobj.loads(key)
        if value == b'':
            value = ''
        else:
            value = javaobj.loads(value)
            if key == 'paymentType':
                print(dir(value))
                value = value.constant
        print(f'{key}:{value}')
    # 立即购买数据解析
    # res = r.get('{BUY_NOW_ORIGIN_DATA_PREFIX}_59')
    # print(res)
    # # res是开发把后台源码中的java对象做了序列化存储后的数据
    # # 我们要将其转成python中的对象
    # # pip install javaobj-py3 -i https://pypi.douban.com/simple
    # res_object = javaobj.loads(res)
    # print(res_object)
    # print(type(res_object))
    # buy_now_object = res_object[0]
    # # buy_now_object这个对象到底都有哪些信息，需需要问开发
    # # python中可以使用dir方法来看对象属性
    # print(dir(buy_now_object))
    # print(buy_now_object.__getattribute__('skuId'))
    # print(buy_now_object.__getattribute__('num'))
