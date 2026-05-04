from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import os, shutil, uuid
from app.database import get_db
from app.models.task import Task, TaskStatus, task_assignments
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskComplete, TaskOut
from app.api.deps import get_current_user, require_pult_or_admin

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

MEDIA_DIR = os.getenv("MEDIA_DIR", "/home/kasper/kasper-management/media")

@router.get("", response_model=List[TaskOut])
def list_tasks(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Task)
    if current_user.role == UserRole.hr:
        q = q.filter(Task.assignees.any(User.id == current_user.id))
    if type:
        q = q.filter(Task.type == type)
    if status:
        q = q.filter(Task.status == status)
    if date_from:
        q = q.filter(Task.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        q = q.filter(Task.created_at <= datetime.combine(date_to, datetime.max.time()))
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()

@router.post("", response_model=TaskOut)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    if not data.assigned_to_ids:
        raise HTTPException(status_code=400, detail="Укажите хотя бы одного исполнителя")
    assignees = db.query(User).filter(User.id.in_(data.assigned_to_ids)).all()
    if len(assignees) != len(data.assigned_to_ids):
        raise HTTPException(status_code=404, detail="Один или несколько пользователей не найдены")
    task = Task(
        title=data.title,
        description=data.description,
        type=data.type,
        due_date=data.due_date,
        created_by_id=current_user.id,
    )
    task.assignees = assignees
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(
    task_id: int,
    data: TaskComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    if current_user.role == UserRole.hr:
        if not any(u.id == current_user.id for u in task.assignees):
            raise HTTPException(status_code=403, detail="Не ваша задача")
    task.status = TaskStatus.done
    task.completion_comment = data.completion_comment
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/complete-media", response_model=TaskOut)
async def complete_with_media(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    if current_user.role == UserRole.hr:
        if not any(u.id == current_user.id for u in task.assignees):
            raise HTTPException(status_code=403, detail="Не ваша задача")
    os.makedirs(MEDIA_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"task_{task_id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, unique_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    if task.completion_media:
        old = os.path.join(MEDIA_DIR, task.completion_media)
        if os.path.exists(old):
            os.remove(old)
    task.completion_media = unique_name
    task.status = TaskStatus.done
    db.commit()
    db.refresh(task)
    return task

@router.post("/{task_id}/reopen", response_model=TaskOut)
def reopen_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    task.status = TaskStatus.pending
    task.completion_comment = None
    task.completion_media = None
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Не найдено")
    if task.completion_media:
        path = os.path.join(MEDIA_DIR, task.completion_media)
        if os.path.exists(path):
            os.remove(path)
    db.delete(task)
    db.commit()
    return {"detail": "Удалено"}
