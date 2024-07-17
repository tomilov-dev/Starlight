from pydantic import BaseModel, EmailStr


class RegisterUserDTO(BaseModel):
    username: str
    password: str
    email: EmailStr


class AuthUserDTO(BaseModel):
    username: str
    password: str


class UserDTO(BaseModel):
    username: str
    email: EmailStr
    active: bool = True


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
