"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from bson import ObjectId

from ..database import get_database
from ..models.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
)
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证管理"])


def user_helper(user) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "full_name": user.get("full_name"),
        "role": user.get("role"),
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """用户登录"""
    db = get_database()
    
    user = await db.users.find_one({"username": login_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    if not verify_password(login_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """用户注册"""
    db = get_database()
    
    # Check if username already exists
    existing = await db.users.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    now = datetime.now()
    user_dict = {
        "username": user_data.username,
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
        "role": user_data.role.value,
        "is_active": user_data.is_active,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await db.users.insert_one(user_dict)
    created = await db.users.find_one({"_id": result.inserted_id})
    return user_helper(created)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return user_helper(current_user)


@router.post("/init-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def init_admin():
    """初始化管理员账户（仅当没有用户时可用）"""
    db = get_database()
    
    # Check if any user exists
    user_count = await db.users.count_documents({})
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统已初始化，无法创建默认管理员",
        )
    
    now = datetime.now()
    admin_dict = {
        "username": "admin",
        "full_name": "系统管理员",
        "hashed_password": get_password_hash("admin123"),
        "role": "管理员",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await db.users.insert_one(admin_dict)
    created = await db.users.find_one({"_id": result.inserted_id})
    return user_helper(created)
