import json


class AuthData:
    def __init__(self):
        # Переменные класса (поля)
        self.username: str = ""
        self.password: str = ""

    def parse_json(self, json_input: str):
        try:
            # Превращаем строку в словарь (dict)
            data = json.loads(json_input)

            # Записываем значения в переменные класса
            self.username = str(data.get("username", ""))
            self.password = str(data.get("password", ""))

            print("Парсинг успешен")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Ошибка парсинга: {e}")


# Пример использования:
#raw_json = '{"username": "ivan_ivanov", "password": "secure_password123"}'
#auth = AuthData()
#auth.parse_json(raw_json)

#print(f"Имя: {auth.username}")
#print(f"Пароль: {auth.password}")

