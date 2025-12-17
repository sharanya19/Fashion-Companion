from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .. import models, schemas, database, config
from ..services import style_analysis
import json

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create profile
    new_profile = models.UserProfile(user_id=new_user.id, full_name=user.full_name)
    db.add(new_profile)
    
    # Run initial analysis
    analysis_data = style_analysis.analyze_user_style(user.email)
    new_analysis = models.UserStyleAnalysis(
        user_id=new_user.id,
        season=analysis_data["season"],
        season_subtype=analysis_data["season_subtype"],
        
        # Serialize Rich Objects to JSON
        skin_tone=json.dumps(analysis_data["skin_tone"]),
        
        undertone=analysis_data["undertone"],
        confidence_score=analysis_data["confidence_score"],
        
        best_colors=json.dumps(analysis_data["best_colors"]),
        neutral_colors=json.dumps(analysis_data["neutral_colors"]),
        worst_colors=json.dumps(analysis_data["worst_colors"]),
        
        # Store Accent Colors in Complementary bucket
        complementary_colors=json.dumps(analysis_data["accent_colors"]),
        
        # Serialize Rich Objects to JSON
        eye_color=json.dumps(analysis_data["eye_color"]),
        hair_color=json.dumps(analysis_data["hair_color"]),
        
        jewelry_metals=json.dumps(analysis_data["jewelry_metals"]),
        jewelry_stones=json.dumps(analysis_data["jewelry_stones"]),
        
        face_shape=analysis_data["face_shape"]
    )
    db.add(new_analysis)
    
    db.commit()
    return new_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
