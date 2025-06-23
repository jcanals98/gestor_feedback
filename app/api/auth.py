from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.utils.dependencies import get_current_user  
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.db.session import SessionLocal
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/me")
def read_current_user(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):

    user = create_user(db, user)

    return user


@router.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user.email, user.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({"sub": user.email})

    return {"acces_token": token, "token_type": "bearer"}
