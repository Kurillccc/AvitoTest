import requests

url = "http://host.docker.internal:8080/api/auth"


data = {
    "username": "your_username",
    "password": "your_password"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    token = response.json().get("token")
    print("Токен:", token)
else:
    print("Ошибка авторизации:", response.status_code, response.text)
