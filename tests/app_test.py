# import pytest
# from app import app, db
# from app.models import User
#
# @pytest.fixture
# def app():
#     # Настройка приложения для тестов
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/kurillccc_test'
#     app.config['TESTING'] = True
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     with app.app_context():
#         db.create_all()  # Создание таблиц для тестов
#     yield app
#     with app.app_context():
#         db.drop_all()  # Очистка базы данных после тестов
#
# @pytest.fixture
# def client(app):
#     return app.test_client()
#
#
