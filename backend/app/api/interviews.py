from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os, shutil, uuid
from app.database import get_db
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

MEDIA_DIR = os.getenv("MEDIA_DIR", "/home/kasper/kasper-management/media")

@router.get("", response_model=List[InterviewOut])
def list_interviews(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Interview)
    if status:
        q = q.filter(Interview.status == status)
    return q.order_by(Interview.scheduled_at.asc().nullslast()).all()

@router.post("", response_model=InterviewOut)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
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
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
    db.commit()
    db.refresh(interview)
    return interview

@router.post("/{interview_id}/complete", response_model=InterviewOut)
def complete_interview(
    interview_id: int,
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    interview.status = 'completed'
    if result:
        interview.result = result
    db.commit()
    db.refresh(interview)
    return interview

@router.post("/{interview_id}/photo", response_model=InterviewOut)
async def upload_photo(
    interview_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"interview_{interview_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, unique_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    if interview.photo_path:
        old_path = os.path.join(MEDIA_DIR, interview.photo_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    interview.photo_path = unique_name
    db.commit()
    db.refresh(interview)
    return interview

@router.get("/photo/{filename}")
def get_photo(filename: str):
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(interview)
    db.commit()
    return {"detail": "Удалено"}
