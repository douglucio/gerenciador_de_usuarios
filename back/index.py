from ast import If
from flask import Flask, jsonify, request
import pymysql
import json
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)


db = pymysql.connect(host="localhost", user="root", password="123456", database="db_teste")

hello = [{"msg":"Hello World"}]
@app.route("/hello", methods=['GET'])
def hello_world():
    return jsonify(hello)

@app.route("/hello", methods=['POST'])
def post_hello_world():
    data = request.get_json()
    pw_hash = bcrypt.generate_password_hash(data.get('pwd')).decode('utf-8')
    cursor = db.cursor()
    sql = "INSERT INTO users (name_us, email_us, pwd_us, perfil_us) values (%s,%s,%s,%s)"
    cursor.execute(sql,(data.get('name'),data.get('email'),pw_hash,data.get('perfil')))
    db.commit()
    msg = {"name": data.get('name'), "email":data.get('email'),"pwd":pw_hash,"perfil":data.get('perfil')}
    return msg

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    pwd_form = data.get('pwd')
    cursor = db.cursor()
    sql = "SELECT * FROM users WHERE email_us = %s"
    cursor.execute(sql,(data.get('email')))
    db.commit()
    results = cursor.fetchone()
    pwd_db = bytes(results[4])
    if bcrypt.check_password_hash(pwd_db.encode('utf-8'),pwd_form):
        print("oi")
    return results[4]

