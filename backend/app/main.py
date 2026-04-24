from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="Wikiio API",
    description="Wikiio 数据分析平台 API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Wikiio API 运行正常", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}