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

## 💡 Возникшие проблемы и их решение:
1. Была поставлена задача "сгруппированную информацию о перемещении монеток в его кошельке",
для ее решения создается отдельная таблица по нескольким причинам: проще и быстрее находить 
нужные транзакции, можно легко добавить нужное поле, а также это сделано с целью, чтобы архитектура 
была более "чистой" – пользователи и транзакции отдельно друг от друга
2. 
