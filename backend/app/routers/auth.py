import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse,
    TokenResponse, RegisterResponse, MessageResponse,
)
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, generate_random_code
)
from app.utils.email import send_verification_email, send_verification_resend_email
from app.config import settings
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=RegisterResponse, status_code=201)
@limiter.limit("3/minute")
async def register(request: Request, data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册 — 创建账户并发送邮箱验证邮件"""

    # 检查邮箱是否已被注册
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 检查用户名是否已被使用
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    # 生成验证 token 和过期时间
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS
    )

    # 创建新用户（未验证邮箱）
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        email_verify_token=token,
        email_verify_token_expires_at=expires_at,
        is_email_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 发送验证邮件
    await send_verification_email(user.email, user.username, token)

    return RegisterResponse(
        message="注册成功，请检查你的邮箱并点击验证链接以激活账户",
        email=user.email,
    )

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

    if not user.is_email_verified:
        raise HTTPException(
            status_code=403,
            detail="邮箱尚未验证，请检查收件箱（包括垃圾邮件）并点击验证链接",
        )

    # 生成JWT token
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token, user=user)

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """验证邮箱（POST，防邮件安全网关自动扫描）"""

    result = await db.execute(
        select(User).where(User.email_verify_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="验证链接无效")

    # 检查 token 是否过期
    if (
        user.email_verify_token_expires_at
        and user.email_verify_token_expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="验证链接已过期，请重新发送验证邮件")

    if user.is_email_verified:
        return MessageResponse(message="邮箱已验证，无需重复操作")

    user.is_email_verified = True
    user.email_verify_token = None
    user.email_verify_token_expires_at = None
    # 将用户角色从 0（未验证）提升为 1（已验证用户）
    if user.role < 1:
        user.role = 1
    await db.commit()

    return MessageResponse(message="邮箱验证成功，现在可以登录了")


@router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit("3/hour")
async def resend_verification(
    request: Request,
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """重发验证邮件"""

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 静默返回，防止用户枚举攻击
    if not user:
        return MessageResponse(
            message="如果该邮箱已注册，验证邮件已重新发送，请检查收件箱"
        )

    if user.is_email_verified:
        raise HTTPException(status_code=400, detail="该邮箱已完成验证，无需重复操作")

    # 生成新 token 和新过期时间
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS
    )
    user.email_verify_token = token
    user.email_verify_token_expires_at = expires_at
    await db.commit()

    await send_verification_resend_email(user.email, user.username, token)

    return MessageResponse(
        message="验证邮件已重新发送，请检查收件箱（包括垃圾邮件文件夹）"
    )