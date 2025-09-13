from pydantic import BaseModel, EmailStr

class LoginRequestDTO(BaseModel):
    email: EmailStr
    password: str

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangePasswordDTO(BaseModel):
    new_password: str
    old_password: str