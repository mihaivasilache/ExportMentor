import mysql.connector


class DbConnection:
    def __init__(self, db_credentials):
        self.host = db_credentials['host']
        self.user = db_credentials['user']
        self.passwd = db_credentials['passwd']
        self.db = db_credentials['db']
        self.db_conn = self.connect()
        self.cursor = self.db_conn.cursor()

    def connect(self):
        db_conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.db
        )
        return db_conn

    def close(self):
        self.cursor.close()
        self.db_conn.close()
