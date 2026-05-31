from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, generate_random_code
)
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
async def register(request: Request, data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""

    # 检查邮箱是否已被注册
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 检查用户名是否已被使用
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    # 创建新用户
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        email_verify_token=generate_random_code(),
        is_email_verified=False,
    )
    db.add(user)
    await db.flush()  # 获取新用户的id

    # TODO: 发送验证邮件（邮件配置完成后再接入）

    return user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""

    # 查找用户
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # 验证用户存在且密码正确
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 生成JWT token
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token, user=user)

@router.get("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """验证邮箱"""

    result = await db.execute(
        select(User).where(User.email_verify_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="验证链接无效或已过期")

    if user.is_email_verified:
        return {"message": "邮箱已经验证过了"}

    user.is_email_verified = True
    user.email_verify_token = None

    return {"message": "邮箱验证成功"}