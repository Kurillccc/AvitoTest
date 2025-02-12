from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"  # Токен будет шифроваться этим ключом

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def home():
    return "Welcome to the Avito Shop API!"

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Проверка на существование пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Пустой ответ, чтобы не было ошибки

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц в базе данных
    app.run(debug=True)

