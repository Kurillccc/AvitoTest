import pytest
from run import app, db
from app.models import User, Transaction, Merch

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
    data = {
        "username": "test",
        "password": "testpass",
        "balance": 1000
    }

    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert response.get_json()["msg"] == "User created successfully"


    response = client.post('/login', json={
        "username": data["username"],
        "password": data["password"]
    })
    assert response.status_code == 200
    access_token = response.get_json()["access_token"]

    with app.app_context():
        user_before = User.query.filter_by(username=data["username"]).first()
        print(f"\nBalance before: {user_before.balance}")

    with app.app_context():
        # Создаем товар
        item = Merch(name="t-shirt", price=20)
        db.session.add(item)
        db.session.commit()

    # Покупка товара
    response = client.post('/buy', json={"item_name": item.name}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Purchase successful"

    with app.app_context():
        user_after = User.query.filter_by(username=data["username"]).first()
        print(f"\nBalance after: {user_after.balance}")
        assert user_after.balance == user_before.balance - item.price
