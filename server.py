import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from hashlib import sha256
from modules.login import Login
from modules.signin import Signin
from modules.pick import Pick
from modules.hashtable import industry, bindustry, bizdic, gcds, sggs, emds
from modules.analyze import Analysis
from modules.recommand import Recommand
from modules.secret import KEY
server = Flask(__name__)
server.secret_key = KEY
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
            session['username'] = ID
            session['token'] = True
            return redirect(url_for('pick'))
        else:
            return redirect(url_for('index', match=False))
    return render_template("index.html", title="로그인", match=match)


@server.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('token', None)
    return redirect(url_for('index'))


@server.route("/signin", methods=['GET', 'POST'])
def signin():
    match = request.args.get('match', default=None)
    if request.method == "POST":
        ID = request.form.get('ID')
        PW = sha256(request.form.get('PW').encode()).hexdigest()
        STOCK = request.form.get('SM')  # 자본금
        # 선호 업종 : 중분류-대분류
        PB = request.form.get('biz')
        # 선호 지역 : 광역시도-시군구-읍면동
        PA = f"{request.form.get('gcd')}-{request.form.get('sgg')}-{request.form.get('emd')}"
        si = Signin(ID)
        if si.comparison() == True:
            si.signin(ID, PW, STOCK, PB, PA, PA, PB)
            si.conn.close()
            return redirect(url_for('signin', match=True))
        else:
            si.conn.close()
            return redirect(url_for('signin', match=False))
    return render_template("sign.html", title="회원가입", match=match, bizdic=bizdic, gcds=gcds, sggs=sggs, emds=emds)


@server.route("/pick", methods=['GET', 'POST'])
def pick():
    match = None
    if 'username' in session:
        ID = session['username']
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    # 정보가져오기
    pk = Pick(ID)
    data = pk.getData()
    if data['기본정보'] == None:
        return redirect(url_for('index'))
    else:
        return render_template("pick.html", title="선택창", match=match, data=data)

# 업종 분석


@server.route("/ind-analyze-1", methods=['POST', 'GET'])
def ind_analyze1():
    match = None
    if 'token' in session:
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    if request.method == "POST":
        loc = f"{request.form.get('gcd')}-{request.form.get('sgg')}-{request.form.get('emd')}"
        return redirect(url_for('ind_analyze2', loc=loc))
    return render_template("ind_analyze1.html", title="업종 분석", gcds=gcds, sggs=sggs, emds=emds)


@server.route("/ind-analyze-2", methods=['POST', 'GET'])
def ind_analyze2():
    match = None
    if 'token' in session:
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    l = request.args.get('loc', default=None)

    ba = Analysis(location=l)
    r1 = ba.b_analysis()
    r2 = ba.getIncomeandAge()
    rd1 = [(k, v) for k, v in r1.items()]
    rd2 = [(title, item) for title, item in zip(
        ['업종별 가장 많은 소비자 추정 소득구간', '업종별 가장 많은 소비자 연령'], r2)]

    # ba.drawBar("biz")
    return render_template("ind_analyze2.html", title=f"'{l}' 업종 분석", result1=rd1, result2=rd2)


@server.route("/loc-analyze-1", methods=['POST', 'GET'])
def loc_analyze1():
    match = None
    if 'token' in session:
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    if request.method == "POST":
        # 대분류 0, 중분류 1
        bmajor = request.form.get('bmajor')
        mmajor = request.form.get('mmajor')
        dic1 = {v: k for k, v in bindustry.items()}
        dic2 = {v: k for k, v in industry.items()}
        return redirect(url_for('loc_analyze2', major1=dic1[bmajor], major2=dic2[mmajor]))
    return render_template("loc_analyze1.html", title="상권 분석", major=bizdic)


@server.route("/loc-analyze-2", methods=['POST', 'GET'])
def loc_analyze2():
    match = None
    if 'token' in session:
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    m1 = int(request.args.get('major1', default=None))
    m2 = int(request.args.get('major2', default=None))
    ma = Analysis(major=(int(m1), int(m2)))
    r = ma.l_analysis()
    ma.drawBar()
    r = ma.l_analysis()
    return render_template("loc_analyze2.html", title=f"{bindustry[m1]}-{industry[m2]} 업종 상권분석", result=r)


@server.route("/b-recommand-1", methods=['POST', 'GET'])
def b_recommand1():
    match = None
    if 'token' in session:
        ID = session['username']
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    if request.method == "POST":
        ID = request.form.get('ID', default=None)
        r = Recommand(ID)
        r.setting()
        r.modeling()
        return redirect(url_for('b_recommand2', rank1=r.result[0], rank2=r.result[1], rank3=r.result[2], rank4=r.result[3], rank5=r.result[4]))
    return render_template("b_recommand1.html", title='업종 추천', ID=ID)


@server.route("/b-recommand-2", methods=['POST', 'GET'])
def b_recommand2():
    match = None
    if 'token' in session:
        match = session['token']
        ID = session['username']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    results = [request.args.get('rank1', default=None),
               request.args.get('rank2', default=None),
               request.args.get('rank3', default=None),
               request.args.get('rank4', default=None),
               request.args.get('rank5', default=None)]
    pk = Pick(ID)
    data = pk.getData()
    if None in results:
        return redirect(url_for('b_recommand1'))
    return render_template("b_recommand2.html", title='사용자 맞춤 업종 추천', results=[(idx+1, i.split('-')[0], i.split('-')[1]) for idx, i in enumerate(results)], data=data)


@server.route("/l-recommand-1", methods=['POST', 'GET'])
def l_recommand1():
    match = None
    if 'token' in session:
        ID = session['username']
        match = session['token']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    if request.method == "POST":
        ID = request.form.get('ID', default=None)
        r = Recommand(ID)
        r.setting('상권')
        r.modeling()
        return redirect(url_for('l_recommand2', rank1=r.result[0], rank2=r.result[1], rank3=r.result[2], rank4=r.result[3], rank5=r.result[4]))
    return render_template("l_recommand1.html", title='상권 추천', ID=ID)


@server.route("/l-recommand-2", methods=['POST', 'GET'])
def l_recommand2():
    match = None
    if 'token' in session:
        match = session['token']
        ID = session['username']
    if match != True:  # 불법적인 접근 시 로그인으로
        return redirect(url_for('index'))
    results = [request.args.get('rank1', default=None),
               request.args.get('rank2', default=None),
               request.args.get('rank3', default=None),
               request.args.get('rank4', default=None),
               request.args.get('rank5', default=None)]
    pk = Pick(ID)
    data = pk.getData()
    if None in results:
        return redirect(url_for('l_recommand1'))
    return render_template("l_recommand2.html", title='사용자 맞춤 상권 추천', results=[(idx+1, i.split('-')[0], i.split('-')[1], i.split('-')[2]) for idx, i in enumerate(results)], data=data)


if __name__ == "__main__":
    server.run('0.0.0.0', port=5010, debug=True)
