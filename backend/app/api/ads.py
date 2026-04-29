from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.ad import Ad, AdPlatform
from app.schemas.ad import AdCreate, AdUpdate, AdOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/ads", tags=["ads"])

@router.get("", response_model=List[AdOut])
def list_ads(
    platform: Optional[AdPlatform] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Ad)
    if platform:
        q = q.filter(Ad.platform == platform)
    return q.order_by(Ad.published_at.desc().nullslast()).all()

@router.post("", response_model=AdOut)
def create_ad(
    data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = Ad(**data.model_dump(), created_by_id=current_user.id)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@router.patch("/{ad_id}", response_model=AdOut)
def update_ad(
    ad_id: int,
    data: AdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(ad)
    db.commit()
    return {"detail": "Удалено"}
