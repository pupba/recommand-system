import os
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from hashlib import sha256
from modules.login import Login
from modules.signin import Signin
from modules.pick import Pick
from modules.hashtable import major_list
from modules.analyze import Analysis
from modules.recommand import Recommand
server = Flask(__name__)
Bootstrap(server)


@server.route("/", methods=['GET', 'POST'])
def index():
    match = request.args.get('match', default=None)
    if request.method == "POST":  # 로그인
        ID = request.form.get('ID')
        # 패스워드는 sha2로 암호화
        PW = sha256(request.form.get('PW').encode()).hexdigest()
        lg = Login(ID, PW)
        # 로그인
        result = lg.comparison()
        if result == True:
            # 로그인 성공
            return redirect(url_for('pick', match=True, ID=ID))
        else:
            return redirect(url_for('index', match=False))
    return render_template("index.html", title="로그인", match=match)


@server.route("/signin", methods=['GET', 'POST'])
def signin():
    match = request.args.get('match', default=None)
    if request.method == "POST":
        ID = request.form.get('ID')
        PW = sha256(request.form.get('PW').encode()).hexdigest()
        STOCK = request.form.get('stock')
        PB = request.form.get('PB')
        PA = request.form.get('PA')
        si = Signin(ID)
        if si.comparison() == True:
            si.signin(ID, PW, STOCK, PB, PA)
            si.conn.close()
            return redirect(url_for('signin', match=True))
        else:
            si.conn.close()
            return redirect(url_for('signin', match=False))
    return render_template("sign.html", title="회원가입", match=match)


@server.route("/pick", methods=['GET', 'POST'])
def pick():
    match = request.args.get('match', default=None)
    ID = request.args.get('ID')
    if ID == None:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    # 정보가져오기
    pk = Pick(ID)
    data = pk.getData()
    print(data)
    return render_template("pick.html", title="선택창", match=match, data=data)


@server.route("/ind-analyze-1", methods=['POST', 'GET'])
def ind_analyze1():
    return render_template("ind_analyze1.html", title="업종 분석", major_list=major_list)


@server.route("/ind-analyze-2", methods=['POST', 'GET'])
def ind_analyze2():
    # r = Recommand("test2")
    # r.setting("상권")
    # r.modeling()
    # print(r.result)
    loc = "전라남도-목포시-연동"
    ba = Analysis(location=loc)
    r1 = ba.b_analysis()

    r2 = ba.getIncomeandAge()

    rd1 = [(k, v) for k, v in r1.items()]
    rd2 = [(title, item) for title, item in zip(
        ['업종별 가장 많은 소비자 추정 소득구간', '업종별 가장 많은 소비자 연령'], r2)]
    # ba.drawBar()
    # ba.drawBar("biz")
    return render_template("ind_analyze2.html", title=f"'{loc}' 업종 분석", result1=rd1, result2=rd2)


@server.route("/loc-analyze-1", methods=['POST', 'GET'])
def loc_analyze1():
    return render_template("loc_analyze1.html")


@server.route("/loc-analyze-2", methods=['POST', 'GET'])
def loc_analyze2():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, 'static', 'analysis', 'loc')
    file_names = os.listdir(folder_path)
    major = (4, 43)
    ma = Analysis(major=major)
    r = ma.l_analysis()
    return render_template("loc_analyze2.html", title="상권분석", result=r, filenames=file_names)


if __name__ == "__main__":
    server.run('0.0.0.0', port=5010, debug=True)
