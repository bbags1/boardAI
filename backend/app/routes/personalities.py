from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..schemas.advisors import PersonalityCreate, PersonalityResponse
from ..models.personality import Personality
from ..db.session import get_db
from ..core.security import get_current_user

router = APIRouter()

@router.post("/create", response_model=PersonalityResponse)
def create_personality(
    personality: PersonalityCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_personality = Personality(
        name=personality.name,
        description=personality.description,
        prompt_template=personality.prompt_template,
        organization_id=current_user.organization_id
    )
    db.add(db_personality)
    try:
        db.commit()
        db.refresh(db_personality)
        return db_personality
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create personality: {str(e)}"
        )

@router.get("/list", response_model=List[PersonalityResponse])
def list_personalities(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Personality).filter(
        Personality.organization_id == current_user.organization_id
    ).all()

@router.delete("/{personality_id}")
def delete_personality(
    personality_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    personality = db.query(Personality).filter(
        Personality.id == personality_id,
        Personality.organization_id == current_user.organization_id
    ).first()
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")
    db.delete(personality)
    db.commit()
    return {"message": "Personality deleted"}