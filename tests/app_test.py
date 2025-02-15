import pytest
from run import app, db
from app.models import User, Transaction, Merch

# Фикстура для инициализации тестового клиента
@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc_test'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Создаем табл перед тестами
    with app.app_context():
        db.create_all()

    # Инициализация клиента
    with app.test_client() as client:
        yield client

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

    with app.app_context():
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


def test_login(client):
    # Сначала создаем пользователя для теста
    with app.app_context():
        user = User(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()

    # Теперь выполняем запрос на логин
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Проверяем, что статус код 200, т.е. запрос успешен
    assert response.status_code == 200

    # Проверяем, что в ответе есть JWT токен
    assert 'access_token' in response.json
    assert isinstance(response.json['access_token'], str)

    # Попробуем войти с неверным паролем
    response_invalid = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    # Проверяем, что ответ с неверными данными возвращает ошибку 401
    assert response_invalid.status_code == 401

    # Проверяем, что в ответе правильное сообщение об ошибке
    assert b'{"msg":"Bad username or password"}\n' in response_invalid.data

def test_register_empty_fields(client):
    response = client.post('/register', json={})
    assert response.status_code == 400
    assert b'Username and password are required' in response.data
