from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from app.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)

    # 站点基本信息
    name = Column(String, nullable=False)           # 站点显示名称，如"中文SCP基金会"
    site_id = Column(String, unique=True, index=True, nullable=False)  # 唯一标识，如"scp-wiki-cn"
    api_url = Column(String, nullable=False)        # MediaWiki API地址
    base_url = Column(String, nullable=False)       # 站点主页地址
    description = Column(Text, nullable=True)       # 站点简介
    language = Column(String, default="zh")         # 语言

    # 爬取配置
    crawl_enabled = Column(Boolean, default=False)  # 是否开启爬取
    crawl_interval = Column(Integer, default=60)    # 增量更新间隔（分钟）
    last_crawled_at = Column(DateTime, nullable=True)  # 上次爬取时间
    crawl_namespaces = Column(String, default="0")  # 爬取的命名空间，默认主命名空间

    # 功能开关
    rating_enabled = Column(Boolean, default=True)  # 是否开放评分
    api_enabled = Column(Boolean, default=False)    # 是否开放Wikiio API

    # 审核状态
    # pending=待审核 approved=已接入 rejected=已拒绝
    status = Column(String, default="pending")
    # 平台类型：fandom 或 miraheze
    platform = Column(String, default="fandom")
    # 是否已启用RatePage扩展
    has_ratepage = Column(Boolean, default=False)

    # 申请人（对应users表的id）
    owner_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())