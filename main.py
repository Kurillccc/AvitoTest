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
    balance = db.Column(db.Integer, default=1000)

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_transactions')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_transactions')

    def __repr__(self):
        return f'<Transaction from {self.sender_id} to {self.receiver_id}, Amount: {self.amount}>'

class Merch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Merch {self.name}, Price: {self.price}>'

def seed_merch():
    merch_items = [
        {"name": "t-shirt", "price": 80},
        {"name": "cup", "price": 20},
        {"name": "book", "price": 50},
        {"name": "pen", "price": 10},
        {"name": "powerbank", "price": 200},
        {"name": "hoody", "price": 300},
        {"name": "umbrella", "price": 200},
        {"name": "socks", "price": 10},
        {"name": "wallet", "price": 50},
        {"name": "pink-hoody", "price": 500}
    ]

    for item in merch_items:
        if not Merch.query.filter_by(name=item["name"]).first():
            db.session.add(Merch(name=item["name"], price=item["price"]))

    db.session.commit()

@app.route('/')
def home():
    return "Welcome to the Avito Shop API!"

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Проверка на существование пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username, password=password, balance=1000)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

# Логин
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Проверка токена
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Передача монет
@app.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    current_user = get_jwt_identity()
    sender = User.query.filter_by(username=current_user).first()

    if not sender:
        return jsonify({"msg": "Sender not found"}), 404

    receiver_username = request.json.get('receiver', None)
    amount = request.json.get('amount', None)

    if not receiver_username or not amount:
        return jsonify({"msg": "Receiver and amount are required"}), 400

    if amount <= 0:
        return jsonify({"msg": "Amount must be positive"}), 400

    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        return jsonify({"msg": "Receiver not found"}), 404

    if sender.balance < amount:
        return jsonify({"msg": "Insufficient funds"}), 400

    # Перевод средств
    sender.balance -= amount
    receiver.balance += amount

    # Запись транзакции
    transaction = Transaction(sender_id=sender.id, receiver_id=receiver.id, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"msg": "Transfer successful", "new_balance": sender.balance}), 200

# Показать транзакции
@app.route('/wallet', methods=['GET'])
@jwt_required()
def wallet():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Получаем историю транзакций
    received = [
        {"from": tx.sender.username, "amount": tx.amount, "timestamp": tx.timestamp}
        for tx in user.received_transactions
    ]

    sent = [
        {"to": tx.receiver.username, "amount": tx.amount, "timestamp": tx.timestamp}
        for tx in user.sent_transactions
    ]

    return jsonify({
        "balance": user.balance,
        "received": received,
        "sent": sent
    }), 200

# Показывает товары в магазине
@app.route('/store', methods=['GET'])
def store():
    merch_list = Merch.query.all()
    return jsonify([{"name": m.name, "price": m.price} for m in merch_list])

# Покупка товаров
@app.route('/buy', methods=['POST'])
@jwt_required()
def buy():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    item_name = request.json.get('item', None)
    if not item_name:
        return jsonify({"msg": "Item name is required"}), 400

    item = Merch.query.filter_by(name=item_name).first()
    if not item:
        return jsonify({"msg": "Item not found"}), 404

    if user.balance < item.price:
        return jsonify({"msg": "Not enough coins"}), 400

    # Списываем монеты
    user.balance -= item.price

    # Записываем покупку
    transaction = Transaction(sender_id=None, receiver_id=user.id, amount=item.price)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"msg": f"Successfully bought {item.name}", "remaining_balance": user.balance}), 200

# Исключаем ошибку в браузере
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Пустой ответ, чтобы не было ошибки

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц в базе данных
    app.run(debug=True)

