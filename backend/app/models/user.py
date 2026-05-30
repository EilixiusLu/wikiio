from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, text
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # 邮箱验证
    is_email_verified = Column(Boolean, default=False)
    email_verify_token = Column(String, nullable=True)

    # Fandom账户绑定
    fandom_username = Column(String, nullable=True)
    fandom_avatar_url = Column(String, nullable=True)
    fandom_verify_code = Column(String, nullable=True)
    is_fandom_verified = Column(Boolean, default=False)

    # Miraheze账户绑定
    miraheze_username = Column(String, nullable=True)
    miraheze_verify_code = Column(String, nullable=True)
    is_miraheze_verified = Column(Boolean, default=False, nullable=False, server_default=text("0"))

    # 用户权限组
    # 0=普通用户 1=已验证用户 2=维基管理员 3=Wikiio管理员
    role = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())