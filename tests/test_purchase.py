import pytest
from run import app, db
from app.models import User, Merch, Transaction

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc_test'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def setup_data():
    with app.app_context():
        user = User(id=1, username="test_user", balance=500)
        merch = Merch(id=1, name="hoody", price=300)
        db.session.add_all([user, merch])
        db.session.commit()

def test_purchase_merch(client, setup_data):
    response = client.post('/purchase', json={"user_id": 1, "merch_id": 1})

    assert response.status_code == 200
    data = response.get_json()

    assert data["message"] == "Purchase successful"

    with app.app_context():
        user = User.query.get(1)
        transaction = Transaction.query.filter_by(sender_id=1).first()

        assert user.balance == 200  # Баланс должен уменьшиться
        assert transaction is not None  # Должна создаться транзакция
        assert transaction.amount == 300  # Сумма корректная
