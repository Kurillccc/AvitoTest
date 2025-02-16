import pytest
from run import app, db
from app.models import User, Transaction

# Фикстура для клиента
@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc_test'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()

def test_transfer(client):
    sender_data = {
        "username": "sender",
        "password": "senderpassword",
        "balance": 1000
    }

    receiver_data = {
        "username": "receiver",
        "password": "receiverpassword",
        "balance": 1000
    }

    response = client.post('/register', json=sender_data)
    assert response.status_code == 201
    assert response.get_json()["msg"] == "User created successfully"

    response = client.post('/register', json=receiver_data)
    assert response.status_code == 201
    assert response.get_json()["msg"] == "User created successfully"

    response = client.post('/login', json={
        "username": sender_data["username"],
        "password": sender_data["password"]
    })
    assert response.status_code == 200
    access_token = response.get_json()["access_token"]

    with app.app_context():
        sender_before = User.query.filter_by(username=sender_data["username"]).first()
        receiver_before = User.query.filter_by(username=receiver_data["username"]).first()
        print(f"\nSender before: {sender_before.balance}, Receiver before: {receiver_before.balance}")

    transfer_data = {
        "receiver": receiver_data["username"],
        "amount": 200
    }

    response = client.post('/transfer', json=transfer_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["msg"] == "Transfer successful"
    assert data["new_balance"] == 800  # Проверяем баланс отправителя

    with app.app_context():
        sender_after = User.query.filter_by(username=sender_data["username"]).first()
        receiver_after = User.query.filter_by(username=receiver_data["username"]).first()
        print(f"Sender after: {sender_after.balance}, Receiver after: {receiver_after.balance}")

    with app.app_context():
        receiver = User.query.filter_by(username=receiver_data["username"]).first()
        print(f"Final receiver balance: {receiver.balance}")
        assert receiver.balance == 1200  # Баланс получателя после

 # Проверяем, что транзакция была записана в базу
def test_transaction_recorded(client):
    sender_data = {
        "username": "sender_tx",
        "password": "senderpassword",
        "balance": 1000
    }

    receiver_data = {
        "username": "receiver_tx",
        "password": "receiverpassword",
        "balance": 500
    }

    client.post('/register', json=sender_data)
    client.post('/register', json=receiver_data)

    response = client.post('/login', json={
        "username": sender_data["username"],
        "password": sender_data["password"]
    })
    access_token = response.get_json()["access_token"]

    transfer_data = {
        "receiver": receiver_data["username"],
        "amount": 300
    }
    client.post('/transfer', json=transfer_data, headers={"Authorization": f"Bearer {access_token}"})

    with app.app_context():
        sender = User.query.filter_by(username=sender_data["username"]).first()
        receiver = User.query.filter_by(username=receiver_data["username"]).first()
        transaction = Transaction.query.filter_by(sender_id=sender.id, receiver_id=receiver.id).first()

        assert transaction is not None, "Транзакция не записалась в БД"
        assert transaction.amount == 300, "Сумма транзакции неверная"
