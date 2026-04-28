from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, UserOut, Token, UserCreate
from app.services.auth import verify_password, hash_password, create_access_token
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/users", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        telegram_id=data.telegram_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/reset-password/{user_id}")
def reset_password(user_id: int, new_password: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"detail": "Пароль сброшен"}

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_manager_or_admin)):
    return db.query(User).order_by(User.full_name).all()
