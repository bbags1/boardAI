from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, Any
from jose import JWTError, jwt  # Add this
from ..core.config import settings  # Add this
from ..core.security import create_access_token, get_password_hash, verify_password
from ..schemas.user import UserCreate, User, Token
from ..models.user import User as UserModel
from ..models.organization import Organization as OrganizationModel
from ..schemas.advisors import UserResponse
from ..db.session import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=User)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(UserModel).filter(UserModel.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get or create organization
    org = db.query(OrganizationModel).filter(
        OrganizationModel.name == user_in.organization_name
    ).first()
    
    if not org:
        org = OrganizationModel(name=user_in.organization_name)
        db.add(org)
        db.commit()
        db.refresh(org)
    
    # Create new user
    db_user = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        organization_id=org.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user