from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

@router.get("", response_model=List[InterviewOut])
def list_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Interview).order_by(Interview.scheduled_at.asc().nullslast()).all()

@router.post("", response_model=InterviewOut)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = Interview(**data.model_dump(), created_by_id=current_user.id)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview

@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    return interview

@router.patch("/{interview_id}", response_model=InterviewOut)
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
    db.commit()
    db.refresh(interview)
    return interview

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.manager:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(interview)
    db.commit()
    return {"detail": "Удалено"}
