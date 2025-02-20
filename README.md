# Avito Shop API (Backend)

## 📝 Описание:
Реализован сервис, который позволяет сотрудникам обмениваться монетками и приобретать на них мерч

## ✨ Функционал:
- Регистрация пользователя (/register)
- Логин и получение токена (/login)
- Проверка авторизации и токена (/protected)
- Отправка монет другому пользователю (/send_coins)
- Покупка мерча (/buy)

## 🤖 Стек:
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended
- pytest

## 💡 Возникшие проблемы и их решение:
1. Была поставлена задача "сгруппировать информацию о перемещении монеток в его кошельке",
для ее решения создается отдельная таблица по нескольким причинам: проще и быстрее находить 
нужные транзакции, можно легко добавить нужное поле, а также это сделано с целью, чтобы архитектура 
была более "чистой" – пользователи и транзакции отдельно друг от друга
2. Непонятно какие тесты конкретно требуется, поэтому написал несколько примитивных тестов для login и register
3. Немного не разобрался с тестированием покупки и перевода

## ⚡ Инструкция по запуску:
1. Клонируем репозиторий (git clone https://github.com/Kurillccc/AvitoTest.git)
2. Перейдите в папку с проектом (cd AvitoTest)
3. Установите зависимости (pip install -r requirements.txt)
4. Запустите файл run (python run)
