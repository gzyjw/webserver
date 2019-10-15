# _*_ coding: utf-8 _*_
import pymysql

HOSTNAME = 'localhost'
DATABASE = 'KMBSDB'
USERNAME = 'root'
PASSWORD = 'gzyjw700829'
DB_URT = 'mysql://{}:{}@{}/{}'.format(USERNAME, PASSWORD, HOSTNAME, DATABASE)

class DB():
    def __init__(self, host = HOSTNAME, port=3306, db=DATABASE, user=USERNAME, passwd=PASSWORD, charset='utf8'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()


if __name__ == '__main__':
    with DB(db=DATABASE) as db:
        #db.execute("INSERT INTO admin_user(name, password) VALUES ('gzyjw', '700829')")
        '''
        userid = 'gzyjw'
        sql = "SELECT * FROM admin_user WHERE userid='%s'" % userid
        db.execute(sql)
        result = db.fetchall()
        for name in result:
            #return 'user is "{user}" password is "{pwd}" '.format(user=userid, pwd = password)
            print("a\n")
        '''
        sql = "SELECT * FROM frm_appversion "
        db.execute(sql)
        result = db.fetchall()
        tempstr = '<p>功能选择：</p><ul>'
        for name in result:
            str = '<li><a href="/choose.html?function=%s">%s</a></li>' % (name['createdBy'] , name['createdBy'])
            tempstr += str
        tempstr += '</ul>'
        print(tempstr)