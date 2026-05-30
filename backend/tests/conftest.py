"""测试配置和共享夹具"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Site, Page, Revision, Rating  # noqa: F401
from app.utils.security import hash_password, create_access_token


# ---------- 数据库 ----------

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """为整个 session 提供一个事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """创建 SQLite 内存引擎（session 级，表结构只建一次）"""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """每个测试函数一个独立数据库会话，事务回滚隔离"""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    TestSessionLocal = async_sessionmaker(
        connection, class_=AsyncSession, expire_on_commit=False
    )
    async with TestSessionLocal() as session:
        yield session
        await transaction.rollback()
        await connection.close()


# ---------- HTTP 客户端 ----------

@pytest_asyncio.fixture
async def client(db_session):
    """FastAPI TestClient，覆盖 get_db 依赖指向测试数据库"""

    async def override_get_db():
        """模拟真实的 get_db：yield session 并在结束后 commit"""
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------- 测试用户 ----------

@pytest_asyncio.fixture
async def test_user(db_session):
    """创建一个普通测试用户并返回 (user, password) 元组"""
    password = "testpass123"
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password(password),
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, password


@pytest_asyncio.fixture
async def admin_user(db_session):
    """创建一个管理员测试用户"""
    password = "adminpass123"
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hash_password(password),
        is_email_verified=True,
        role=3,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, password


@pytest_asyncio.fixture
async def user_headers(test_user):
    """普通用户的 Authorization header"""
    user, _ = test_user
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(admin_user):
    """管理员的 Authorization header"""
    user, _ = admin_user
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------- 测试数据辅助 ----------

@pytest_asyncio.fixture
async def sample_site(db_session, admin_user):
    """创建一个测试站点"""
    site = Site(
        name="测试维基",
        site_id="test-wiki",
        api_url="https://test.fandom.com/api.php",
        base_url="https://test.fandom.com/zh",
        platform="fandom",
        has_ratepage=False,
        status="approved",
        crawl_enabled=True,
        owner_id=admin_user[0].id,
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest_asyncio.fixture
async def sample_pages(db_session, sample_site):
    """创建几篇测试页面"""
    pages_data = [
        {
            "site_id": sample_site.site_id,
            "page_id": 1001,
            "title": "测试页面一",
            "slug": "测试页面一",
            "author": "作者A",
            "author_id": 1,
            "wikitext": "这是第一篇测试页面的正文内容。",
            "word_count": 15,
            "categories": '["故事", "原创"]',
            "rating_count": 2,
            "rating_avg": 4.5,
            "namespace": 0,
        },
        {
            "site_id": sample_site.site_id,
            "page_id": 1002,
            "title": "测试页面二",
            "slug": "测试页面二",
            "author": "作者B",
            "author_id": 2,
            "wikitext": "这是第二篇测试页面的正文内容。包含更多文字用于测试搜索高亮。",
            "word_count": 25,
            "categories": '["文档", "指南"]',
            "rating_count": 1,
            "rating_avg": 3.0,
            "namespace": 0,
        },
        {
            "site_id": sample_site.site_id,
            "page_id": 1003,
            "title": "英文页面",
            "slug": "English_Page",
            "author": "作者A",
            "author_id": 1,
            "wikitext": "This is an English test page.",
            "word_count": 6,
            "categories": '["翻译"]',
            "rating_count": 0,
            "rating_avg": 0.0,
            "namespace": 0,
        },
    ]
    pages = []
    for pd in pages_data:
        page = Page(**pd)
        db_session.add(page)
        pages.append(page)
    await db_session.commit()
    for p in pages:
        await db_session.refresh(p)
    return pages


@pytest_asyncio.fixture
async def fandom_bound_user(db_session, test_user):
    """已绑定 Fandom 的测试用户"""
    user, _ = test_user
    user.is_fandom_verified = True
    user.fandom_username = "FandomUser"
    user.fandom_avatar_url = "https://avatar.url/test.jpg"
    await db_session.commit()
    return user
