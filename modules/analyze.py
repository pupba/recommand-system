from secret import dbconn
# 업종코드 매핑을 위해 import
from hashtable import industry
import pandas as pd


class B_Analysis:
    def __init__(self, location: str):
        self.location = location
        self.conn, self.cursor = dbconn()
        sql = "SELECT * FROM paydata"
        self.__data = pd.read_sql(sql, self.conn)
        self.__result = None

    def b_PayCount(self):
        Pay_count = self.__data.groupby('m_business')['pay_num'].sum()
        return Pay_count

    def b_PayCount_T5(self):
        Pay_count = self.b_PayCount()
        Top5 = Pay_count.nlargest(5)
        return Top5

    def b_PayMoney(self):
        Pay_money = self.__data.groupby('m_business')['pay_money'].sum()
        return Pay_money

    def b_PayMoney_T5(self):
        Pay_money = self.b_PayMoney()
        Top5 = Pay_money.nlargest(5)
        return Top5

    def b_Consumer_income(self):
        Consumer_income = self.__data.groupby('m_business')['income'].apply(
            lambda x: x.value_counts().idxmax())
        return Consumer_income

    def b_Consumer_age(self):
        Consumer_age = self.__data.groupby('m_business')['age'].apply(
            lambda x: x.value_counts().idxmax())
        return Consumer_age

    def analysis(self) -> dict:
        self.__result = {}

        # 업종별 결제건수 분석
        b_Pay_Count = ba.b_PayCount()
        b_Pay_Count.index = b_Pay_Count.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 결제건수"] = b_Pay_Count

        # 업종별 결제건수 TOP5 분석
        b_Pay_Count_Top5 = ba.b_PayCount_T5()
        b_Pay_Count_Top5.index = b_Pay_Count_Top5.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 결제건수 TOP5"] = b_Pay_Count_Top5

        # 업종별 결제금액 분석
        PayMoney = ba.b_PayMoney()
        PayMoney.index = PayMoney.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 결제금액"] = PayMoney

        # 업종별 결제금액 TOP5 분석
        PayMoney_Top5 = ba.b_PayMoney_T5()
        PayMoney_Top5.index = PayMoney_Top5.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 결제금액 TOP5"] = PayMoney_Top5

        # 업종별 가장 많은 소비자 추정 소득구간 분석
        Consumer_income = ba.b_Consumer_income()
        Consumer_income.index = Consumer_income.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 가장 많은 소비자 추정 소득구간"] = Consumer_income

        # 업종별 가장 많은 소비자 연령 분석
        Consumer_age = ba.b_Consumer_age()
        Consumer_age.index = Consumer_age.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__result["업종별 가장 많은 소비자 연령"] = Consumer_age

        return self.__result


if __name__ == "__main__":
    # 업종분석 수행
    ba = B_Analysis("목포")
    result = ba.analysis()
    for i in result:
        print(i)
        print(result[i])
        print()
