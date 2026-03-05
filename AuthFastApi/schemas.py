from pydantic import BaseModel, Field

# 'CryptContext' - это то, что будет использоваться для хэширования и проверки паролей.
from passlib.context import CryptContext

#  функция для хэширования пароля, поступающего от пользователя.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str = Field(default=None, example="")
    token_type: str = Field(default=None, example="")


class User(BaseModel):

    username: str = Field(default=None, example="")
    password: str = Field(default=None, example="")

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Функция для проверки, соответствует ли полученный пароль сохраненному хэшу"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        """Функция генерации хэша пароля"""
        return pwd_context.hash(password)
