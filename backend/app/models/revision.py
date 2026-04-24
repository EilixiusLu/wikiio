from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from app.database import Base

class Revision(Base):
    __tablename__ = "revisions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联页面
    page_id = Column(Integer, index=True, nullable=False)   # 对应pages表的id
    site_id = Column(String, index=True, nullable=False)    # 冗余存储方便查询

    # MediaWiki版本信息
    rev_id = Column(Integer, nullable=False)        # MediaWiki里的版本ID
    parent_rev_id = Column(Integer, nullable=True)  # 上一个版本ID

    # 编辑信息
    editor = Column(String, nullable=True)          # 编辑者用户名
    editor_id = Column(Integer, nullable=True)      # 编辑者MediaWiki用户ID
    comment = Column(String, nullable=True)         # 编辑摘要
    size = Column(Integer, default=0)               # 版本大小（字节）
    size_diff = Column(Integer, default=0)          # 与上一版本的大小差异

    timestamp = Column(DateTime, nullable=False)    # 编辑时间
    created_at = Column(DateTime, server_default=func.now())