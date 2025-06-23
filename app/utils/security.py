from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import jwt, JWTError
from dotenv import load_dotenv
import os


load_dotenv()# Leer variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # valor por defecto si no está


# Contexto para cifrar contraseñas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hasear contraseña antes de guardarla
def hash_password(password : str) -> str:
    return pwd_context.hash(password)

# Verificar si el password que escribió el usuario coincide con el hash de la DB
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Crear un token de acceso JWT válido por X minutos
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    try:
        # 1. Verificamos y decodificamos el token con la clave y el algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extraemos el "sub" (subject), que es el email que guardamos en el token
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta el campo 'sub'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    
    except JWTError:
        # Si el token está mal firmado, ha expirado o no es válido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    