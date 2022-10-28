from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
from models import User
import jwt
from functools import wraps
import datetime
from dotenv import load_dotenv
import os
import pymysql

app = Flask(__name__)
CORS(app)

# configure my secret key
app.config['SECRET_KEY']=os.getenv('MY_SECRET_KEY')

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

#configure database
db = pymysql.connect(host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'), password=os.getenv('DATABASE_PWD'), database=os.getenv('DATABASE_NAME'))

# function for token verification
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
            
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            cursor = db.cursor()
            sql = "SELECT * FROM users WHERE email_us = %s"
            cursor.execute(sql,(data.get('public_id')))
            db.commit()
            current_user = cursor.fetchone()
            #return current_user
        except:
            return jsonify({'message': 'token is invalid'})
          
        return f(current_user, *args, **kwargs)
       

    return decorator

@app.route("/hello", methods=['GET'])
def hello_world():
    return jsonify({"msg" : "Hello Word"})

@app.route("/newuser", methods=['POST'])
@token_required
def new_user(current_user):
    data = request.get_json()
    email = data.get('email')
    pwd = data.get('pwd')
    if len(email) < 1 or len(pwd) < 1:
        return jsonify({"msg" : "os campos Email e Password precisam estar preenchidos"}), 400
    
    cursor = db.cursor()
    sql = "SELECT * FROM users WHERE email_us = %s"
    cursor.execute(sql,(email))
    db.commit()
    results = cursor.fetchone()
    
    if results:
        return jsonify({"msg" : "Email já cadastrado"}), 400
    
    forhash = bytes(pwd,'utf-8')
    pw_hash = bcrypt.hashpw(forhash, bcrypt.gensalt())
    cursor = db.cursor()
    sql = "INSERT INTO users (name_us, email_us, pwd_us, perfil_us) values (%s,%s,%s,%s)"
    cursor.execute(sql,(data.get('name'),email, pw_hash, data.get('perfil')))
    db.commit()
    return jsonify({"msg" : email+" foi cadastrado com sucesso!"}), 201

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('pwd')

    if len(email) < 1 or len(password) < 1:
        return jsonify({"msg" : "os campos Email e Password precisam estar preenchidos"}), 400
    
    forhash = bytes(password,'utf-8')
    cursor = db.cursor()
    sql = "SELECT * FROM users WHERE email_us = %s"
    cursor.execute(sql,(email))
    db.commit()
    results = cursor.fetchone()

    if bcrypt.checkpw(forhash, results[4].encode('utf-8')):
        token = jwt.encode({'public_id': results[0], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'id': results[0], 'name': results[1], 'email': results[2], 'perfil': results[3],'token' : token})
    else:
        return jsonify({"msg" : "Invalid Login Info!"}), 400
        

@app.route('/author', methods=['POST'])
@token_required
def create_author(current_user):
    data = request.get_json() 
    cursor = db.cursor()
    sql = "INSERT INTO authors (name_author, email_author) values (%s,%s)"
    cursor.execute(sql,(data.get('name'),data.get('email')))
    db.commit()
    return f'Author foi cadastrado: {data}', 200 
   