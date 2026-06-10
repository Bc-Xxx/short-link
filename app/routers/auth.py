from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/auth/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(
        username=user.username,
        email=user.email,
        hash_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.model_validate(new_user)


@router.post("/auth/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if not verify_password(user.password, db_user.hash_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    login_user_token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "access_token": login_user_token,
        "token_type": "bearer"
    }
