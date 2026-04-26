from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.form_template import FormTemplate
from app.schemas.form_template import FormTemplateCreate, FormTemplateUpdate, FormTemplateOut
from app.api.deps import get_current_user, require_manager_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("", response_model=List[FormTemplateOut])
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(FormTemplate).order_by(FormTemplate.id.desc()).all()

@router.post("", response_model=FormTemplateOut)
def create_template(
    data: FormTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    template = FormTemplate(
        name=data.name,
        fields=[f.model_dump() for f in data.fields],
        created_by_id=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/{template_id}", response_model=FormTemplateOut)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    return template

@router.patch("/{template_id}", response_model=FormTemplateOut)
def update_template(
    template_id: int,
    data: FormTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    if data.name is not None:
        template.name = data.name
    if data.fields is not None:
        template.fields = [f.model_dump() for f in data.fields]
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    template = db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Не найдено")
    db.delete(template)
    db.commit()
    return {"detail": "Удалено"}
