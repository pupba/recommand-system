from modules.secret import dbconn


class Pick:
    def __init__(self, ID: str):
        self.__ID = ID
        # db 연결
        self.conn, self.cursor = dbconn()

    def getData(self) -> tuple:
        sql = "SELECT * FROM user_info WHERE ID = %s"
        self.cursor.execute(sql, (self.__ID,))
        result = self.cursor.fetchone()
        return tuple([self.__ID]+[i if i != None else "입력 안됨" for i in result[2:-2]])
