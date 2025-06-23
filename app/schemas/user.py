from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

model_config = ConfigDict(from_attributes=True) # Esto es necesario para usar objetos SQLAlchemy como respuesta