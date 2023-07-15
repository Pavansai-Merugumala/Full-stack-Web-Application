from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database file path

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

    def __init__(self, name, price):
        self.name = name
        self.price = price

@app.before_first_request
def create_tables():
    db.create_all()

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)

jwt = JWT(app, authenticate, identity)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User(username, password)
    db.session.add(user)
    db.session.commit()

    return {'message': 'User registered successfully'}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return {'message': 'Invalid username or password'}, 401

    token = jwt.jwt_encode_callback(user)
    return {'token': token.decode('utf-8')}

@app.route('/fooditems', methods=['GET'])
@jwt_required()
def get_food_items():
    food_items = FoodItem.query.all()
    items = [{'name': item.name, 'price': item.price} for item in food_items]
    return {'food_items': items}

if __name__ == '__main__':
    app.run(debug=True)

