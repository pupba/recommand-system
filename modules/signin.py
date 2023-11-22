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

    def signin(self, ID, PW, stock, PB, PA, AS, BS) -> None:
        sql = f"INSERT INTO user_info (ID, PW, Equity, PreArea, PreBus,AreaSearch,BusSearch) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (ID, PW, stock, PB, PA, AS, BS)
        self.cursor.execute(sql, values)
        self.conn.commit()
        sql = "INSERT INTO history(user_id, type, value) VALUES (%s,%s,%s)"
        values1 = (ID, 0, AS)
        values2 = (ID, 1, BS)
        self.cursor.execute(sql, values1)
        self.conn.commit()
        self.cursor.execute(sql, values2)
        self.conn.commit()
        sql = "INSERT INTO major_anal(stock,pre_major,pre_location,search_major) VALUES (%s,%s,%s,%s)"
        value = (stock, PB, PA, BS)
        self.cursor.execute(sql, value)
        sql = "INSERT INTO loc_anal(stock,pre_major,pre_location,search_location) VALUES (%s,%s,%s,%s)"
        value = (stock, PB, PA, AS)
        self.cursor.execute(sql, value)
