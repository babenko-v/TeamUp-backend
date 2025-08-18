from datetime import datetime, timedelta, timezone
import os
from typing import Dict
from jose import JWTError, jwt
from application.auth.interfaces import ITokenService

SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

class JWTService(ITokenService):

    def create_access_token(self, data: Dict) -> str:
        copy_data_to_encode = data.copy()
        expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        copy_data_to_encode.update({"exp": expire_time, "type":"access"})

        return jwt.encode(copy_data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, data: Dict) -> str:
        copy_data_to_encode = data.copy()
        expire_time = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        copy_data_to_encode.update({"exp": expire_time, "type": "refresh"})

        return jwt.encode(copy_data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload

        except JWTError as JWTException:
            raise ValueError(f"Could not decode token - {JWTException}")

