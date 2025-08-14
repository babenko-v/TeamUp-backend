from src.application.auth.interfaces import IPasswordHasher
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHasher(IPasswordHasher):

    @staticmethod
    def verify_password(plain_password: str, hashed_password) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
