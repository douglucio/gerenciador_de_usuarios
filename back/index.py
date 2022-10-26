from flask import Flask, jsonify, request
from db import db
from flask_cors import CORS
import bcrypt
from models import User

app = Flask(__name__)
CORS(app)


hello = [{"msg":"Hello World"}]
@app.route("/hello", methods=['GET'])
def hello_world():
    return jsonify(hello)

@app.route("/hello", methods=['POST'])
def post_hello_world():
    data = request.get_json()
    pwd = data.get('pwd')
    forhash = bytes(pwd,'utf-8')
    email = data.get('email')
    pw_hash = bcrypt.hashpw(forhash, bcrypt.gensalt())
    cursor = db.cursor()
    sql = "INSERT INTO users (name_us, email_us, pwd_us, perfil_us) values (%s,%s,%s,%s)"
    cursor.execute(sql,(data.get('name'),email, pw_hash, data.get('perfil')))
    db.commit()
    return f'Welcome! {email}', 200

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('pwd')
    forhash = bytes(password,'utf-8')
    cursor = db.cursor()
    sql = "SELECT * FROM users WHERE email_us = %s"
    cursor.execute(sql,(email))
    db.commit()
    results = cursor.fetchone()
    if bcrypt.checkpw(forhash, results[4].encode('utf-8')):
        return f'Logged in, Welcome {email}!', 200
    else:
        return 'Invalid Login Info!', 400
   