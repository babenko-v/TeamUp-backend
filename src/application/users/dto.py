from pydantic import BaseModel, EmailStr

class UserDTO(BaseModel): # Add some validation settings
    username: str
    password: str
    email: EmailStr