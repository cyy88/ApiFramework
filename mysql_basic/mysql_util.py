import pymysql


class DBUtil:

    def __init__(self, host, user, password, db, port=3306):
        self.connect = pymysql.Connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def select_all(self, sql):
        cursor = self.connect.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        self.connect.commit()  # 提交事务，如果不提交，那么下次查询，查不到最新的数据
        cursor.close()
        return data

    def update(self, sql):
        """
        insert、update、delete
        :param sql:
        :return:
        """
        cursor = self.connect.cursor()
        cursor.execute(sql)
        self.connect.commit()
        cursor.close()

    def close(self):
        if self.connect is not None:
            self.connect.close()


if __name__ == '__main__':

    db_util = DBUtil(host='rm-bp11onw2yqbq44yel0o.mysql.rds.aliyuncs.com', user='jxt_saas', password='!@#QWEasd', db='jxt_saas')
    res = db_util.select_all('select *  FROM tcom_school where tenant_id = 422')
    print(res)
    db_util.close()

    # db_util = DBUtil(host='82.156.74.26', user='mtxshop_test', password='mtxshamo')
    # res = db_util.select('select *  FROM mtxshop_trade.es_order ORDER BY order_id DESC LIMIT 2')
    # print(res[0]['order_status'])
    # db_util.close()
