# from modules.secret import dbconn
# from secret import dbconn
from modules.secret import dbconn
from modules.pick import Pick
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.utils import to_categorical


class Recommand:
    def __init__(self, user: str) -> None:
        # DB Connect
        self.conn, self.cursor = dbconn()
        # get UserInfo
        self.user = user
        p = Pick(self.user)

        self.usr_data = p.getData()
        self.train = None
        self.target = None
        self.input_pred = None
        self.result = None

    def setting(self, TYPE: str = "업종") -> None:
        lb = LabelEncoder()
        mm = MinMaxScaler()
        if TYPE == "상권":
            sql = "SELECT * FROM loc_anal"
            usr = pd.read_sql(sql, self.conn).iloc[:, [1, 2, 3, 4]]

            sql = "SELECT * FROM hjdcode"
            hjd = pd.read_sql(sql, self.conn)
            hjd_ = hjd.iloc[:, 1]+"-"+hjd.iloc[:, 2]+"-"+hjd.iloc[:, 3]
            # 데이터 샘플링

            sampled_indices = np.random.choice(
                len(hjd_), size=len(usr), replace=False)
            self.target = hjd_[sampled_indices]

            tmp1 = self.usr_data['기본정보']
            tmp2 = self.usr_data['추가정보'][0]
            self.input_pred = pd.DataFrame({
                "stock": tmp1[1] if tmp1[1] != "입력 안됨" else None, "pre_major": tmp1[3] if tmp1[3] != "입력 안됨" else None, "pre_location": tmp1[2] if tmp1[2] != "입력 안됨" else None, "search_location": tmp2}, index=[0])
            for i in ['pre_major', 'pre_location', 'search_location']:
                usr.loc[:, i] = lb.fit_transform(usr.loc[:, i])

                self.input_pred.loc[:, i] = lb.transform(
                    self.input_pred.loc[:, i])
            usr = mm.fit_transform(usr)
            self.train = usr
            self.input_pred = mm.transform(self.input_pred)
        else:  # 업종
            sql = "SELECT * FROM major_anal"
            usr = pd.read_sql(sql, self.conn)
            sql = "SELECT mmajor.id_num,bmajor.main_name,mmajor.sub_name FROM mmajor JOIN bmajor ON mmajor.main_category = bmajor.main_category;"
            b: pd.DataFrame = pd.read_sql(sql, self.conn)
            major = b.iloc[:, 1] + "-" + b.iloc[:, 2]
            sampled_indices = np.random.choice(
                len(major), size=len(usr), replace=False)
            self.target = major[sampled_indices]
            tmp1 = self.usr_data['기본정보']
            tmp2 = self.usr_data['추가정보'][1]
            self.input_pred = pd.DataFrame({
                "stock": tmp1[1] if tmp1[1] != "입력 안됨" else None, "pre_major": tmp1[3] if tmp1[3] != "입력 안됨" else None, "pre_location": tmp1[2] if tmp1[2] != "입력 안됨" else None, "search_major": tmp2}, index=[0])
            for i in ['pre_major', 'pre_location', 'search_major']:
                usr.loc[:, i] = lb.fit_transform(usr.loc[:, i])

                self.input_pred.loc[:, i] = lb.transform(
                    self.input_pred.loc[:, i])
            usr = mm.fit_transform(usr)
            self.train = usr
            self.input_pred = mm.transform(self.input_pred)

    def modeling(self):
        if None in self.input_pred:
            return "sorry"
        # 모델 구성
        model = Sequential()
        model.add(Dense(128, activation='relu', input_shape=(4,)))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(len(self.target), activation='softmax'))

        # 컴파일
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy', metrics=['accuracy'])
        lb = LabelEncoder()
        y = lb.fit_transform(self.target)

        y_encoded = to_categorical(y)
        self.train = self.train.astype(float)

        # 학습
        model.fit(self.train, y_encoded, epochs=10, batch_size=32)

        # 예측
        self.input_pred = self.input_pred.astype(float)
        predict = model.predict(self.input_pred).argsort(axis=1)[:, -5:]

        self.result = lb.inverse_transform(predict[0])


if __name__ == "__main__":
    # r = Recommand("test2")
    # r.setting("상권")
    # r.modeling()
    # print(r.result)
    pass
