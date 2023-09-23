from flask import Flask, request
from flask import render_template
app = Flask(__name__)
database = {"test": "123"}


@app.route("/get_login_page", methods=['GET'])
def get_login_page():
    return render_template('login_page.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        print(request.args)
        account = request.args.get('account')
        password = request.args.get('password')
        print(account)
        print(database)
        if account not in database:
            return "<h1>This account doesn't exist</h1>"
        if database[account] == password:
            return "<h1>Success</h1>"
        else:
            return "<h1>failed</h1>"


@app.route("/get_signup_page", methods=['GET', 'POST'])
def get_signup_page():
    return render_template('signup_page.html')


@app.route("/sign_up", methods=['POST'])
def sign_up():
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('password')
        check_password = request.form.get('check_password')
        if account in database:
            return "<h1>This account already exist</h1>"
        if check_password != password:
            return "<h1>password is not the same</h1>"
        else:
            database[account] = password
            print(database)
            return "<h1>Success</h1>"


app.run()
# app.run(host='0.0.0.0',port=5000,debug=True)
