from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from hashlib import sha256
from modules.login import Login
from modules.signin import Signin
from modules.pick import Pick
from modules.analyze import B_Analysis
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
    return render_template("pick.html", title="선택창", match=match, data=data)


@server.route("/ind-analyze-1", methods=['POST', 'GET'])
def ind_analyze1():
    return render_template("ind_analyze1.html", title="업종 분석")


@server.route("/ind-analyze-2", methods=['POST', 'GET'])
def ind_analyze2():
    return render_template("ind_analyze2.html", title="업종 분석")


if __name__ == "__main__":
    server.run('0.0.0.0', port=5010, debug=True)
