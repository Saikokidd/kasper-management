from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.tiktok_stream import TiktokStream
from app.schemas.tiktok_stream import TiktokStreamCreate, TiktokStreamUpdate, TiktokStreamOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/tiktok-streams", tags=["tiktok_streams"])

@router.get("", response_model=List[TiktokStreamOut])
def list_streams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(TiktokStream).order_by(TiktokStream.stream_date.desc()).all()

@router.post("", response_model=TiktokStreamOut)
def create_stream(
    data: TiktokStreamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    stream = TiktokStream(**data.model_dump(), created_by_id=current_user.id)
    db.add(stream)
    db.commit()
    db.refresh(stream)
    return stream

@router.patch("/{stream_id}", response_model=TiktokStreamOut)
def update_stream(
    stream_id: int,
    data: TiktokStreamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    stream = db.query(TiktokStream).filter(TiktokStream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(stream, field, value)
    db.commit()
    db.refresh(stream)
    return stream

@router.delete("/{stream_id}")
def delete_stream(
    stream_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    stream = db.query(TiktokStream).filter(TiktokStream.id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(stream)
    db.commit()
    return {"detail": "Удалено"}
