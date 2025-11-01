from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.config import settings
from app.utils.auth import verify_password, get_password_hash, create_access_token, verify_token, ph
from app.models.user import User
from app.schemas.auth import Token, UserRegister
from app.schemas.user import UserCreate, UserInDB

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def authenticate_user(db: Session, username: str, password: str):
    """Autenticar usuario"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    # Si el hash del usuario está en un esquema viejo o necesita actualización,
    # re-hashear la contraseña (con el plaintext recién proporcionado) y guardar.
    try:
        # ph.check_needs_rehash devuelve True si el hash debe actualizarse
        if ph.check_needs_rehash(user.hashed_password):
            new_hash = get_password_hash(password)
            user.hashed_password = new_hash
            db.add(user)
            db.commit()
            db.refresh(user)
    except Exception:
        # No fallar la autenticación solo porque la migración automática falló.
        pass
    return user

def get_user_by_username(db: Session, username: str):
    """Obtener usuario por username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Obtener usuario por email"""
    return db.query(User).filter(User.email == email).first()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    try:
        # Crear nuevo usuario
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Crear token de acceso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el usuario"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Iniciar sesión"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtener información del usuario actual"""
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return UserInDB.from_orm(user)