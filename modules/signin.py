from modules.secret import dbconn


class Signin:
    def __init__(self, ID: str) -> None:
        self.__ID = ID
        # db 연결
        self.conn, self.cursor = dbconn()

    def comparison(self) -> bool:
        # 아이디가 존재하는지 확인
        sql = "SELECT COUNT(*) FROM user_info WHERE ID = %s"
        self.cursor.execute(sql, (self.__ID,))

        # 결과 가져오기
        result = self.cursor.fetchone()
        if result[0] < 1:  # 아이디가 없음
            return True
        else:  # 아이디가 있음
            return False

    def signin(self, ID, PW, stock, PB, PA) -> None:
        sql = f"INSERT INTO user_info (ID, PW, Equity, PreArea, PreBus) VALUES (%s,%s,%s,%s,%s)"
        values = (ID, PW, stock, PB, PA)
        self.cursor.execute(sql, values)
        self.conn.commit()
