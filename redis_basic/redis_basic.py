import redis

# decode_responses表示是否针对结果去做decode转码
pool = redis.ConnectionPool(
    host='127.0.0.1',
    port=6379,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)  # 拿到一个操作对象

# 操作字段数据
r.set('name', 'shamo2')  # 向redis存数据，名称是name，值是shamo2
print(r.get('name'))  # 获取name这个key的值

# s = b'shamo2'
# print(type(s))
# s1 = s.decode()
# print(type(s1))

# 操作哈希数据
r.hset('userinfo2', 'name', 'shamo')
r.hset('userinfo2', 'age', '18')
r.hset('userinfo2', 'job', 'tester')
print(r.hgetall('userinfo2'))

# 操作列表
r.lpush('list33', 'data1', 'data2', 'data3')
print(r.lrange('list33', 0, -1))

# 操作集合
r.sadd('jihe33', 'da1', 'da2', 'da3')
print(r.smembers('jihe33'))

# 操作有序集合
r.zadd('zset33', {'data1': 80, 'data2': 70, 'data3': 90})
print(r.zrange('zset33', 0, -1))

r.delete('key1')
r.exists('key1')  # 判断是否存在
r.expire('jihe33', 10000)

# 获取某一个key所对应的redis的数据类型
print(r.type('zset33'))  # zset
print(r.type('jihe33'))  # set
print(r.type('list33'))  # list
print(r.type('userinfo2'))  # hash
print(r.type('name'))  # string
