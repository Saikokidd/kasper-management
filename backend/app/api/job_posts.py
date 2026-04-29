from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.job_post import JobPost, JobPlatform
from app.schemas.job_post import JobPostCreate, JobPostUpdate, JobPostOut
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/job-posts", tags=["job_posts"])

@router.get("", response_model=List[JobPostOut])
def list_job_posts(
    platform: Optional[JobPlatform] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(JobPost)
    if platform:
        q = q.filter(JobPost.platform == platform)
    return q.order_by(JobPost.created_at.desc()).all()

@router.post("", response_model=JobPostOut)
def create_job_post(
    data: JobPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = JobPost(**data.model_dump(), created_by_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.patch("/{post_id}", response_model=JobPostOut)
def update_job_post(
    post_id: int,
    data: JobPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = db.query(JobPost).filter(JobPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Не найдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_job_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.pult:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    post = db.query(JobPost).filter(JobPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(post)
    db.commit()
    return {"detail": "Удалено"}
