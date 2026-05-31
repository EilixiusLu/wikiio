import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.config import settings
from app.routers import auth, users, sites, pages, search, ratings, admin
from app.utils.logger import access_logger, error_logger

app = FastAPI(
    title="Wikiio API",
    description="Wikiio 数据分析平台 API",
    version="0.1.0"
)

# 注入 limiter 到 app.state（slowapi 需要）
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------- CORS ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 访问日志 ----------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每一次API请求"""
    start = time.time()
    try:
        response = await call_next(request)
        duration = round((time.time() - start) * 1000)
        access_logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration}ms "
            f"ip={request.client.host}"
        )
        return response
    except Exception as e:
        error_logger.error(
            f"{request.method} {request.url.path} "
            f"error={str(e)} "
            f"ip={request.client.host}"
        )
        raise

# ---------- 路由 ----------

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(pages.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(ratings.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# ---------- 根路径 ----------

@app.get("/")
async def root():
    return {"message": "Wikiio API 运行正常", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
