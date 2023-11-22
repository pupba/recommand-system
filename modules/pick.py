from modules.secret import dbconn
# from secret import dbconn


class Pick:
    def __init__(self, ID: str):
        self.__ID = ID
        # db 연결
        self.conn, self.cursor = dbconn()

    def getData(self) -> dict:
        # 기본정보 : 선호
        sql = "SELECT * FROM user_info WHERE ID = %s"
        self.cursor.execute(sql, (self.__ID,))
        result = self.cursor.fetchone()
        # 추가정보 : 검색 기록 -> 제일 많이 검색(상권 0,업종 1)
        # 0
        sql1 = f"SELECT value FROM history WHERE user_id = '{self.__ID}' AND type = 0 GROUP BY value ORDER BY COUNT(*) DESC LIMIT 1;"
        self.cursor.execute(sql1)
        r1 = self.cursor.fetchone()[0]

        # 1
        sql2 = f"SELECT value FROM history WHERE user_id = '{self.__ID}' AND type = 1 GROUP BY value ORDER BY COUNT(*) DESC LIMIT 1;"
        self.cursor.execute(sql2)
        r2 = self.cursor.fetchone()[0]

        if r1 != None or r2 != None:
            re = {"기본정보": tuple(
                [self.__ID]+[i if i != None else "입력 안됨" for i in result[2:-2]]), "추가정보": (r1, r2)}
            return re
        else:
            return {'기본정보': None}
