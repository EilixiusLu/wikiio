from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, func, ForeignKey
from app.database import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)

    # 所属站点
    site_id = Column(String, index=True, nullable=False)  # 对应sites表的site_id字段

    # 页面基本信息
    page_id = Column(Integer, nullable=False)       # MediaWiki里的页面ID
    title = Column(String, nullable=False, index=True)  # 页面标题
    slug = Column(String, nullable=False, index=True)   # 页面URL名称

    # 作者（首个版本创建者）
    author = Column(String, nullable=True)
    author_id = Column(Integer, nullable=True)      # MediaWiki用户ID

    # 内容信息
    wikitext = Column(Text, nullable=True)          # 页面Wikitext原文
    word_count = Column(Integer, default=0)         # 字数统计
    categories = Column(Text, nullable=True)        # 分类，JSON格式存储
    tags = Column(Text, nullable=True)              # 标签，JSON格式存储

    # 评分统计（冗余存储，避免每次实时计算）
    rating_count = Column(Integer, default=0)       # 评分人数
    rating_avg = Column(Float, default=0.0)         # 平均评分

    # 原站 RatePage 评分（已归一化为10分制）
    site_rating_avg = Column(Float, nullable=True)      # 原站平均评分
    site_rating_count = Column(Integer, default=0)      # 原站评分人数

    # 页面状态
    is_redirect = Column(Boolean, default=False)    # 是否是重定向页面
    namespace = Column(Integer, default=0)          # 命名空间

    # 爬取时间
    first_crawled_at = Column(DateTime, server_default=func.now())
    last_crawled_at = Column(DateTime, server_default=func.now())
    last_edited_at = Column(DateTime, nullable=True)  # 页面在wiki上的最后编辑时间