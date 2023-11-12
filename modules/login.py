from modules.secret import dbconn


class Login:
    def __init__(self, ID: str, PW: str) -> None:
        self.__ID = ID
        self.__PW = PW
        # db 연결
        self.conn, self.cursor = dbconn()

    def comparison(self) -> bool:
        # 아이디가 존재하는지 확인
        sql = "SELECT COUNT(*) FROM user_info WHERE ID = %s"
        self.cursor.execute(sql, (self.__ID,))

        # 결과 가져오기
        result = self.cursor.fetchone()
        if result[0] < 1:
            self.conn.close()
            return False
        else:
            # 비교하기
            sql = "SELECT PW FROM user_info WHERE ID = %s"
            self.cursor.execute(sql, (self.__ID,))
            # 결과 가져오기
            result = self.cursor.fetchone()
            self.conn.close()
            if result[0] == self.__PW:
                return True
            else:
                return False
