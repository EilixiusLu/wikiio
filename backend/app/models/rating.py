from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    user_id = Column(Integer, index=True, nullable=False)   # 对应users表的id
    page_id = Column(Integer, index=True, nullable=False)   # 对应pages表的id
    site_id = Column(String, index=True, nullable=False)    # 冗余存储

    # 评分内容
    score = Column(Integer, nullable=False)                 # 1-5星

    # 修改历史
    previous_score = Column(Integer, nullable=True)         # 上一次的评分
    updated_count = Column(Integer, default=0)              # 修改次数

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 确保同一用户对同一页面只能有一条评分记录
    __table_args__ = (
        UniqueConstraint("user_id", "page_id", name="uq_user_page_rating"),
    )