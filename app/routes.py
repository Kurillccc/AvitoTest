from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Transaction, Merch

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return "Welcome to the Avito Shop API!"

# Регистрация
@bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if len(username) > 100:
        return jsonify({"msg": "Username is too long"}), 400

    # Проверка на существование пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username, password=password, balance=1000)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

# Логин
@bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Проверка токена
@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Передача монет
@bp.route('/transfer', methods=['POST'])
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
@bp.route('/wallet', methods=['GET'])
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
@bp.route('/store', methods=['GET'])
def store():
    merch_list = Merch.query.all()
    return jsonify([{"name": m.name, "price": m.price} for m in merch_list])

# Покупка товаров
@bp.route('/buy', methods=['POST'])
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
@bp.route('/favicon.ico')
def favicon():
    return '', 204  # Пустой ответ, чтобы не было ошибки