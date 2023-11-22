# from hashtable import industry
from matplotlib.font_manager import FontProperties
import pandas as pd
from modules.hashtable import industry
from modules.secret import dbconn
# from secret import dbconn
import seaborn as sns
import matplotlib.pyplot as plt
# mac m1 gpu 에러해결을 위한 코드
import matplotlib
from flask import url_for
matplotlib.use('agg')
# 업종코드 매핑을 위해 import
font_prop = FontProperties(fname='./static/font/nexon.ttf')


class Analysis:
    def __init__(self, location: str = None, major: tuple = None):
        self.conn, self.cursor = dbconn()
        sql = "SELECT * FROM paydata"
        # 결제 데이터
        self.__data: pd.DataFrame = pd.read_sql(sql, self.conn)
        # 미확인 데이터가 있는 레코드 삭제
        self.__data = self.__data[(self.__data["b_business"] != 99) &
                                  (self.__data["m_business"] != 99) &
                                  (self.__data["income"] != 99)]
        # 행정동 코드
        sql = "SELECT * FROM hjdcode"
        self.__hjd: pd.DataFrame = pd.read_sql(sql, self.conn)
        if location != None:
            self.location = location
            self.__b_result = None

            # 읍면동 매핑을 위한 테이블
            hashTable = {int(
                self.__hjd.iloc[i].loc["hcode"]): f"{self.__hjd.iloc[i].loc['sdm']}-{self.__hjd.iloc[i].loc['sgg']}-{self.__hjd.iloc[i].loc['emd']}" for i in self.__hjd.index}
            tmp = self.__data.copy(deep=True)
            tmp.loc[:, 'emd'] = tmp.loc[:, 'emd'].map(
                hashTable)
            self.__b_data = tmp[tmp.loc[:, 'emd'] == location]
        if major != None:
            self.major = major
            self.__l_data_g = {k: v for k, v in self.__data.copy(
                deep=True).groupby('megalopolis')}
            self.__l_result = None
        # 대분류 코드, 중분류 코드
        sql = "SELECT * FROM bmajor"
        self.bmajor = pd.read_sql(sql, self.conn).to_dict()['main_name']
        sql = "SELECT * FROM mmajor"
        self.mmajor = pd.read_sql(
            sql, self.conn).loc[:, ["sub_category", "sub_name"]]

        self.mmajorl = dict(
            zip(self.mmajor['sub_category'], self.mmajor['sub_name']))

    """ ---------- 업종 분석 ------------ """

    def b_PayCount(self): return self.__b_data.groupby(
        'm_business')['pay_num'].sum()

    def b_PayCount_T5(self):
        Pay_count = self.b_PayCount()
        Top5 = Pay_count.nlargest(5)
        return Top5

    def b_PayMoney(self):
        return self.__b_data.groupby('m_business')['pay_money'].sum()

    def b_PayMoney_T5(self):
        Pay_money = self.b_PayMoney()
        Top5 = Pay_money.nlargest(5)
        return Top5

    def b_Consumer_income(self):
        Consumer_income = self.__b_data.groupby('m_business')['income'].apply(
            lambda x: x.value_counts().idxmax())
        return Consumer_income

    def b_Consumer_age(self):
        Consumer_age = self.__b_data.groupby('m_business')['age'].apply(
            lambda x: x.value_counts().idxmax())
        return Consumer_age

    def b_analysis(self) -> dict:
        self.__b_result = {}
        # 업종별 결제건수 분석
        b_Pay_Count = self.b_PayCount()
        b_Pay_Count.index = b_Pay_Count.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 결제건수 (건)"] = b_Pay_Count

        # 업종별 결제건수 TOP5 분석
        b_Pay_Count_Top5 = self.b_PayCount_T5()
        b_Pay_Count_Top5.index = b_Pay_Count_Top5.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 결제건수 TOP5 (간)"] = b_Pay_Count_Top5

        # 업종별 결제금액 분석
        PayMoney = self.b_PayMoney()
        PayMoney.index = PayMoney.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 결제금액 (만 원)"] = PayMoney

        # 업종별 결제금액 TOP5 분석
        PayMoney_Top5 = self.b_PayMoney_T5()
        PayMoney_Top5.index = PayMoney_Top5.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 결제금액 TOP5 (만 원)"] = PayMoney_Top5

        # 업종별 가장 많은 소비자 추정 소득구간 분석
        Consumer_income = self.b_Consumer_income()
        Consumer_income.index = Consumer_income.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 가장 많은 소비자 추정 소득구간"] = Consumer_income

        # 업종별 가장 많은 소비자 연령 분석
        Consumer_age = self.b_Consumer_age()
        Consumer_age.index = Consumer_age.index.map(
            lambda x: industry.get(x, "알 수 없음"))
        self.__b_result["업종별 가장 많은 소비자 연령"] = Consumer_age

        return self.__b_result

    """ ---------- 상권 분석 ------------ """

    def convert_code_to_region(self, code: str):
        region_info = self.__hjd[self.__hjd['hcode'] == code]
        if len(region_info) > 0:
            return ' '.join(region_info[['sdm', 'sgg', 'emd']].values[0])
        else:
            return '해당 지역 코드 정보가 없습니다.'
    # 업종대분류코드에 따른 결제건수가 가장 많은 지역(TOP5)를 찾는 함수

    def top5_payment_count_major(self, industry_major: int, data_g: pd.DataFrame) -> dict:
        data = data_g[data_g['b_business'] == industry_major]
        top5_count = data.groupby('emd')['pay_num'].sum().nlargest(5)
        return ((self.convert_code_to_region(str(code)), count) for code, count in top5_count.items())

    # 업종대분류코드에 따른 결제금액이 가장 많은 지역(TOP5)를 찾는 함수

    def top5_payment_amount_major(self, industry_major: int, data_g: pd.DataFrame) -> dict:
        data = data_g[data_g['b_business'] == industry_major]
        top5_amount = data.groupby('emd')['pay_money'].sum().nlargest(5)
        return ((self.convert_code_to_region(str(code)), amount) for code, amount in top5_amount.items())

    # 업종중분류코드에 따른 결제건수가 가장 많은 지역(TOP5)를 찾는 함수

    def top5_payment_count_minor(self, industry_minor: int, data_g: pd.DataFrame) -> dict:
        data = data_g[data_g['m_business'] == industry_minor]
        top5_count = data.groupby('emd')['pay_num'].sum().nlargest(5)
        return ((self.convert_code_to_region(str(code)), count) for code, count in top5_count.items())

    # 업종중분류코드에 따른 결제금액이 가장 많은 지역(TOP5)를 찾는 함수

    def top5_payment_amount_minor(self, industry_minor: int, data_g: pd.DataFrame) -> dict:
        data = data_g[data_g['m_business'] == industry_minor]
        top5_amount = data.groupby('emd')['pay_money'].sum().nlargest(5)
        return ((self.convert_code_to_region(str(code)), amount) for code, amount in top5_amount.items())

    def l_analysis(self) -> tuple:
        self.__l_result = []
        for doe, data in self.__l_data_g.items():
            mask = self.__hjd.loc[:, 'hcode'].astype(
                str).str.startswith(str(doe)[:2])
            d = self.__hjd[mask].iloc[0, 1]

            title = [f"{d} 내 {self.bmajor[self.major[0]-1]} 업종(대분류) 결제건수가 가장 많은 TOP 5 구역",
                     f"{d} 내 {self.bmajor[self.major[0]-1]} 업종(대분류) 결제금액이 가장 많은 TOP 5 구역",
                     f"{d} 내 {self.mmajorl[self.major[1]]} 업종(중분류) 결제건수가 가장 많은 TOP 5 구역",
                     f"{d} 내 {self.mmajorl[self.major[1]]} 업종(중분류) 결제금액이 가장 많은 TOP 5 구역"]

            values = [self.top5_payment_count_major(self.major[0], data.copy(deep=True)),
                      self.top5_payment_amount_major(
                          self.major[0], data.copy(deep=True)),
                      self.top5_payment_count_minor(
                          self.major[1], data.copy(deep=True)),
                      self.top5_payment_amount_minor(self.major[1], data.copy(deep=True))]
            tmp = {i: k for i, k in zip(title, values)}

            self.__l_result.append(tmp)
        return tuple(self.__l_result)

    def drawBar(self, TYPE: str = None):
        def drawPlot(**args):
            idx = args['idx']
            figs = args['figs']
            plots = args['plots']
            title = args['title']
            x = args['x']
            y = args['y']

            plots[idx].set_title(title, fontproperties=font_prop)
            plots[idx].set_xlabel("건수" if idx in [1, 3]
                                  else "만 원", fontproperties=font_prop)
            plots[idx].set_ylabel("업종(대분류)" if idx in [
                                  0, 1] else "업종(중분류)", fontproperties=font_prop)
            plots[idx].set_yticklabels(x, fontproperties=font_prop)
            plots[idx].set_ylim(5, 10)
            sns.barplot(x=y, y=x, hue=y, palette='Set3',
                        legend=False, ax=plots[idx], orient='h')
            if idx == 1:
                figs[0].tight_layout()
                figs[0].savefig(
                    f"./static/results/loc/{title.split()[0]}_{'대분류'}.png")
            if idx == 3:
                figs[1].tight_layout()
                figs[1].savefig(
                    f"./static/results/loc/{title.split()[0]}_{'중분류'}.png")
                plots[0].cla()
                plots[1].cla()
                plots[2].cla()
                plots[3].cla()

        sns.set(style="whitegrid")
        fig1, axs1 = plt.subplots(1, 2, figsize=(15, 8))
        fig2, axs2 = plt.subplots(1, 2, figsize=(15, 8))
        plots = (axs1[0], axs1[1], axs2[0], axs2[1])
        if TYPE == "biz":

            for idx, key in enumerate(list(self.__b_result.keys())[:-2]):
                x = self.__b_result[key].index
                y = self.__b_result[key]

                plots[idx].set_title(key, fontproperties=font_prop)
                plots[idx].set_xlabel(
                    "만 원" if idx in [2, 3] else "건수", fontproperties=font_prop)
                plots[idx].set_ylabel("구역", fontproperties=font_prop)
                plots[idx].set_ylim(5, 10)
                plots[idx].set_yticklabels(x, fontproperties=font_prop)
                sns.barplot(x=y, y=x, hue=y, palette='Set3',
                            legend=False, ax=plots[idx], orient='h')

                if idx == 1:
                    fig1.tight_layout()
                    fig1.savefig(
                        f"./static/results/biz/{'결제건수'}.png"
                    )
                if idx == 3:
                    fig2.tight_layout()
                    fig2.savefig(
                        f"./static/results/biz/{'결제금액'}.png"
                    )
        else:
            for doe in self.__l_result:
                for idx, (title, data) in enumerate(doe.items()):
                    x = []
                    y = []
                    for i in data:
                        x.append(i[0])
                        y.append(i[1])
                    drawPlot(idx=idx, figs=(fig1, fig2),
                             plots=plots, title=title, x=x, y=y)

    def getIncomeandAge(self) -> None:
        result = []
        for idx, key in enumerate(list(self.__b_result.keys())[-2:]):
            data = self.__b_result[key]
            if idx == 0:  # 소득구간
                table = {2: "3천만원 미만", 3: "5천만원 미만",
                         4: "7천만원 미만", 5: "1억원 미만", 6: "1억원 이상"}
                result.append(data.map(table))
            else:  # 연령
                result.append(data.apply(lambda x: str(x*10)+' 대'))
        return result


if __name__ == "__main__":
    # 업종분석 수행
    # ba = Analysis(location="전라남도-목포시-연동", major=(4, 43))
    # r1 = ba.b_analysis()

    # r2 = ba.l_analysis()
    # # print(ba.getIncomeandAge())
    # ba.drawBar()
    # ba.drawBar("biz")
    pass
