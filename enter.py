from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_all_tables, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
import json

# 1. Настройка Базы Данных PostgreSQL
# Формат: postgresql://логин:пароль@хост:порт/название_бд
DATABASE_URL = "postgresql://user:password@localhost:5432/my_database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. Модель пользователя в БД
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# Создаем таблицы
Base.metadata.create_all(bind=engine)

# 3. Настройка безопасности (хэширование)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# 4. FastAPI приложение и схемы данных
app = FastAPI()




class AuthData: #json
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
raw_json = '{"username": "ivan_ivanov", "password": "secure_password123"}'
auth = AuthData()
auth.parse_json(raw_json)

print(f"Имя: {auth.username}")
print(f"Пароль: {auth.password}")


class UserAuth(BaseModel):
    username: str
    password: str


# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login_or_register(user_data: UserAuth, db: Session = Depends(get_db)):
    # Ищем пользователя в базе
    user = db.query(User).filter(User.username == user_data.username).first()

    if user:
        # Если пользователь есть, проверяем пароль
        if verify_password(user_data.password, user.hashed_password):
            return {"message": f"Авторизация успешна. Добро пожаловать, {user.username}!"}
        else:
            raise HTTPException(status_code=401, detail="Неверный пароль")

    else:
        # Если пользователя нет, регистрируем его
        new_user = User(
            username=user_data.username,
            hashed_password=hash_password(user_data.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Пользователь не найден. Регистрация прошла успешно!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
