from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# Configuración para hashear contraseñas con Argon2
ph = PasswordHasher()

# Configuración de seguridad
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña con Argon2 PasswordHasher."""
    if plain_password is None:
        return False
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        # cualquier otro error, no verificar
        return False

def get_password_hash(password: str) -> str:
    """Hashear contraseña con Argon2."""
    if password is None:
        raise ValueError("password must be a non-empty string")
    if not isinstance(password, str):
        password = str(password)
    try:
        return ph.hash(password)
    except Exception as exc:
        raise ValueError(f"failed to hash password: {exc}") from exc


def _truncate_password_for_bcrypt(password: str, max_bytes: int = 72) -> str:
    """Trunca una contraseña para que su representación en bytes UTF-8 no
    exceda max_bytes (por defecto 72). Devuelve una cadena segura para
    pasar a bcrypt.

    Nota: bcrypt solo procesa los primeros 72 bytes de la contraseña, por
    lo que truncamos explícitamente para evitar que passlib/bcrypt lance
    una excepción en contraseñas muy largas.
    """
    if password is None:
        raise ValueError("password must be a string")

    if not isinstance(password, str):
        # For safety, coerce to str
        password = str(password)

    b = password.encode('utf-8')
    if len(b) <= max_bytes:
        return password

    truncated = b[:max_bytes]
    # Decodificar ignorando bytes inválidos para no romper multibyte chars
    return truncated.decode('utf-8', errors='ignore')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verificar token JWT y retornar el usuario"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Obtener usuario actual autenticado"""
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user