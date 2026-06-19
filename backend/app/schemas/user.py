from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

# 注册时前端发来的数据格式
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("用户名至少3个字符")
        if len(v) > 20:
            raise ValueError("用户名最多20个字符")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v):
        if len(v) < 8:
            raise ValueError("密码至少8个字符")
        return v

# 登录时前端发来的数据格式
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 返回给前端的用户信息格式
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_email_verified: bool
    is_fandom_verified: bool = False
    fandom_username: Optional[str] = None
    fandom_avatar_url: Optional[str] = None
    miraheze_username: Optional[str] = None
    is_miraheze_verified: bool = False
    role: int
    created_at: datetime

    model_config = {"from_attributes": True}

# 注册成功后返回的数据格式（不再返回 JWT，需验证邮箱后才能登录）
class RegisterResponse(BaseModel):
    message: str
    email: str

# 邮箱验证 / 重发验证邮件后的通用响应
class MessageResponse(BaseModel):
    message: str

# 登录成功后返回的数据格式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse