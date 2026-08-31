from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefreshRequest,
    UserOut,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies.auth import get_current_user, require_business, require_customer

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _create_user(data: UserRegister, role: UserRole, db: Session) -> User:
    """Helper to avoid duplicating registration logic."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_customer(payload: UserRegister, db: Session = Depends(get_db)):
    return _create_user(payload, UserRole.CUSTOMER, db)


@router.post(
    "/register-business",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_business(payload: UserRegister, db: Session = Depends(get_db)):
    return _create_user(payload, UserRole.BUSINESS, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.query(User).filter(User.id == decoded.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    token_data = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.get("/business-only")
def test_business(user: User = Depends(require_business)):
    return {"message": f"Welcome Business User: {user.email}"}


@router.get("/customer-only")
def test_customer(user: User = Depends(require_customer)):
    return {"message": f"Welcome Customer: {user.email}"}