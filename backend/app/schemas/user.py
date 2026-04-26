from pydantic import BaseModel
from app.models.user import UserRole

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.hr
    telegram_id: str | None = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    telegram_id: str | None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
