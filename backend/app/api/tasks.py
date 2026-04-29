from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.task import Task, TaskTemplate, TaskStatus
from app.models.user import User, UserRole
from app.schemas.task import TaskCreate, TaskComplete, TaskOut, TaskTemplateCreate, TaskTemplateOut
from app.api.deps import get_current_user, require_pult_or_admin

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/templates", response_model=List[TaskTemplateOut])
def list_task_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(TaskTemplate).order_by(TaskTemplate.id.desc()).all()

@router.post("/templates", response_model=TaskTemplateOut)
def create_task_template(
    data: TaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    tmpl = TaskTemplate(**data.model_dump(), created_by_id=current_user.id)
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl

@router.delete("/templates/{tmpl_id}")
def delete_task_template(
    tmpl_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    tmpl = db.query(TaskTemplate).filter(TaskTemplate.id == tmpl_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(tmpl)
    db.commit()
    return {"detail": "Удалено"}

@router.get("", response_model=List[TaskOut])
def list_tasks(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Task)
    if current_user.role == UserRole.hr:
        q = q.filter(Task.assigned_to_id == current_user.id)
    if type:
        q = q.filter(Task.type == type)
    if status:
        q = q.filter(Task.status == status)
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()

@router.post("", response_model=TaskOut)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pult_or_admin)
):
    assigned = db.query(User).filter(User.id == data.assigned_to_id).first()
    if not assigned:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    task = Task(**data.model_dump(), created_by_id=current_user.id)
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
    if current_user.role == UserRole.hr and task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Не ваша задача")
    task.status = TaskStatus.done
    task.completion_comment = data.completion_comment
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
    db.delete(task)
    db.commit()
    return {"detail": "Удалено"}
