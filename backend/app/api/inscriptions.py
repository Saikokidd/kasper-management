from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.inscription import Inscription
from app.schemas.inscription import InscriptionCreate, InscriptionUpdate, InscriptionOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/inscriptions", tags=["inscriptions"])

@router.get("", response_model=List[InscriptionOut])
def list_inscriptions(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Inscription)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Inscription.full_name.ilike(like),
            Inscription.username.ilike(like),
            Inscription.phone.ilike(like),
        ))
    return q.order_by(Inscription.created_at.desc()).all()

@router.post("", response_model=InscriptionOut)
def create_inscription(
    data: InscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = Inscription(**data.model_dump(), created_by_id=current_user.id)
    db.add(inscription)
    db.commit()
    db.refresh(inscription)
    return inscription

@router.patch("/{inscription_id}", response_model=InscriptionOut)
def update_inscription(
    inscription_id: int,
    data: InscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = db.query(Inscription).filter(Inscription.id == inscription_id).first()
    if not inscription:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inscription, field, value)
    db.commit()
    db.refresh(inscription)
    return inscription

@router.delete("/{inscription_id}")
def delete_inscription(
    inscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    inscription = db.query(Inscription).filter(Inscription.id == inscription_id).first()
    if not inscription:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(inscription)
    db.commit()
    return {"detail": "Удалено"}
