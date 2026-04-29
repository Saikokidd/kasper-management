from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.database import get_db
from app.models.candidate import Candidate
from app.models.form_template import FormTemplate
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

@router.get("", response_model=List[CandidateOut])
def list_candidates(
    search: Optional[str] = Query(None),
    template_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Candidate)
    if search:
        q = q.filter(Candidate.full_name.ilike(f"%{search}%"))
    if template_id:
        q = q.filter(Candidate.template_id == template_id)
    return q.order_by(Candidate.created_at.desc()).all()

@router.post("", response_model=CandidateOut)
def create_candidate(
    data: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    template = db.query(FormTemplate).filter(FormTemplate.id == data.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    candidate = Candidate(
        full_name=data.full_name,
        template_id=data.template_id,
        fields=data.fields,
        created_by_id=current_user.id
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    return candidate

@router.patch("/{candidate_id}", response_model=CandidateOut)
def update_candidate(
    candidate_id: int,
    data: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    if data.full_name is not None:
        candidate.full_name = data.full_name
    if data.fields is not None:
        candidate.fields = data.fields
    db.commit()
    db.refresh(candidate)
    return candidate

@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(candidate)
    db.commit()
    return {"detail": "Удалено"}
