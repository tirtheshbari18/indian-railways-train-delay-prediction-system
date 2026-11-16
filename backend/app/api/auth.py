from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token, get_current_user_payload
from backend.app.models.schema import User, AuditLog
from backend.app.schemas.pydantic_models import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )
    
    # Assign role: default is viewer, first user or explicit admin role
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role if user_in.role in ["admin", "analyst", "viewer"] else "viewer",
        hashed_password=get_password_hash(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Token
    token = create_access_token({"sub": user.username, "role": user.role, "email": user.email})
    
    # Audit log
    audit = AuditLog(
        username=user.username,
        action="USER_REGISTERED",
        entity_type="USER",
        entity_id=str(user.id),
        details={"email": user.email, "role": user.role}
    )
    db.add(audit)
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_in.username).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated."
        )

    token = create_access_token({"sub": user.username, "role": user.role, "email": user.email})
    
    audit = AuditLog(
        username=user.username,
        action="LOGIN_SUCCESS",
        entity_type="USER",
        entity_id=str(user.id),
        details={"role": user.role}
    )
    db.add(audit)
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(payload: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    username = payload.get("sub")
    if not username or payload.get("anonymous"):
        # Return guest profile
        return UserResponse(
            id=0,
            username="guest",
            email="guest@railway.local",
            full_name="Guest Passenger",
            role="viewer",
            is_active=True,
            created_at=datetime.utcnow()
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
