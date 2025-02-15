import pytest
from run import app, db
from app.models import User, Transaction, Merch

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc_test'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Создаем табл перед тестами
    with app.app_context():
        db.create_all()
    yield app.test_client()
    # Удаляем табл после тестов
    with app.app_context():
        db.drop_all()

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    assert b'User created successfully' in response.data

    # Проверка добавления в бд
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'

def test_register_duplicate(client):
    client.post('/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'newpassword'
    })
    assert response.status_code == 400
    assert b'User already exists' in response.data
