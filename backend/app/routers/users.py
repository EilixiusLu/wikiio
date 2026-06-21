from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.security import decode_access_token, generate_random_code
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import httpx

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["用户"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """从JWT token中获取当前登录用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的登录凭证")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return user

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user

@router.post("/fandom/bind/start")
async def fandom_bind_start(
    fandom_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """第一步：生成验证码，告诉用户去哪里填写"""

    if current_user.is_fandom_verified:
        raise HTTPException(status_code=400, detail="已经绑定了Fandom账户")

    # 检查该Fandom用户名是否已被其他Wikiio用户绑定
    result = await db.execute(
        select(User).where(
            User.fandom_username == fandom_username,
            User.is_fandom_verified == True
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该Fandom账户已被其他用户绑定")

    # 生成验证码
    verify_code = generate_random_code(16)

    current_user.fandom_username = fandom_username
    current_user.fandom_verify_code = verify_code
    await db.commit()

    return {
        "verify_code": verify_code,
        "instruction": f"请在 Fandom 上编辑以下页面，将验证码填入页面内容中",
        "target_page": f"User:{fandom_username}/wikiio-verify",
        "target_url": f"https://community.fandom.com/wiki/User:{fandom_username}/wikiio-verify",
    }

@router.post("/fandom/bind/verify")
async def fandom_bind_verify(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """第二步：验证用户是否已在Fandom页面填写了验证码"""

    if current_user.is_fandom_verified:
        raise HTTPException(status_code=400, detail="已经绑定了Fandom账户")

    if not current_user.fandom_username or not current_user.fandom_verify_code:
        raise HTTPException(status_code=400, detail="请先发起绑定申请")

    fandom_username = current_user.fandom_username
    verify_code = current_user.fandom_verify_code

    # 通过MediaWiki API读取用户验证页面内容
    api_url = "https://community.fandom.com/api.php"
    page_title = f"User:{fandom_username}/wikiio-verify"

    try:
        headers = {
            "User-Agent": "Wikiio/1.0 (Wiki data analysis platform; https://github.com/EilixiusLu/wikiio)"
        }
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            response = await client.get(api_url, params={
                "action": "query",
                "titles": page_title,
                "prop": "revisions",
                "rvprop": "content",
                "rvlimit": 1,
                "format": "json",
                "utf8": "1",
            })
            data = response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"无法连接到Fandom API: {str(e)}")

    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))

    if "missing" in page:
        raise HTTPException(
            status_code=400,
            detail=f"找不到页面 {page_title}，请确认已创建该页面"
        )

    revisions = page.get("revisions", [])
    if not revisions:
        raise HTTPException(status_code=400, detail="页面内容为空")

    page_content = revisions[0].get("*", "") or revisions[0].get("content", "")

    if verify_code not in page_content:
        raise HTTPException(
            status_code=400,
            detail="验证码不匹配，请确认已将验证码填入页面"
        )

    # 验证成功，获取Fandom头像
    avatar_url = await get_fandom_avatar(fandom_username)

    current_user.is_fandom_verified = True
    current_user.fandom_verify_code = None
    current_user.fandom_avatar_url = avatar_url
    current_user.role = max(current_user.role, 1)  # 升级为已验证用户
    await db.commit()

    return {
        "message": "Fandom账户绑定成功！",
        "fandom_username": fandom_username,
        "avatar_url": avatar_url,
    }

async def get_fandom_avatar(username: str) -> str:
    """通过Fandom services API获取用户头像"""
    try:
        # 先通过MediaWiki API获取用户ID
        async with httpx.AsyncClient(timeout=10, headers={
            "User-Agent": "Wikiio/1.0 (Wiki data analysis platform; https://github.com/EilixiusLu/wikiio)"
        }) as client:
            r = await client.get(
                "https://community.fandom.com/api.php",
                params={
                    "action": "query",
                    "list": "users",
                    "ususers": username,
                    "format": "json",
                }
            )
            data = r.json()
            users = data.get("query", {}).get("users", [])
            if not users or "userid" not in users[0]:
                return ""
            user_id = users[0]["userid"]

        # 再通过services API获取头像
        async with httpx.AsyncClient(timeout=10, headers={
            "User-Agent": "Wikiio/1.0 (Wiki data analysis platform; https://github.com/EilixiusLu/wikiio)"
        }) as client:
            r = await client.get(
                f"https://services.fandom.com/user-attribute/user/{user_id}/attr/avatar",
                headers={"Accept": "application/json"}
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("value", "")
    except Exception as e:
        logger.error(f"获取Fandom头像失败: {e}")
    return ""

@router.delete("/fandom/unbind")
async def fandom_unbind(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """解绑Fandom账户"""
    current_user.fandom_username = None
    current_user.fandom_avatar_url = None
    current_user.fandom_verify_code = None
    current_user.is_fandom_verified = False
    # 解绑后降为普通用户，但不影响管理员权限（role>=2保持不变）
    if current_user.role < 2:
        current_user.role = 0
    await db.commit()
    return {"message": "已解绑Fandom账户"}

@router.post("/miraheze/bind/start")
async def miraheze_bind_start(
    miraheze_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """第一步：生成Miraheze验证码"""
    if current_user.is_miraheze_verified:
        raise HTTPException(status_code=400, detail="已经绑定了Miraheze账户")

    # 检查是否已被其他用户绑定
    result = await db.execute(
        select(User).where(
            User.miraheze_username == miraheze_username,
            User.is_miraheze_verified == True
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该Miraheze账户已被其他用户绑定")

    verify_code = generate_random_code(16)
    current_user.miraheze_username = miraheze_username
    current_user.miraheze_verify_code = verify_code
    await db.commit()

    return {
        "verify_code": verify_code,
        "instruction": "请在 Miraheze Meta 上编辑以下页面，将验证码填入页面内容中",
        "target_page": f"User:{miraheze_username}/wikiio-verify",
        "target_url": f"https://meta.miraheze.org/wiki/User:{miraheze_username}/wikiio-verify",
    }

@router.post("/miraheze/bind/verify")
async def miraheze_bind_verify(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """第二步：验证Miraheze页面上的验证码"""
    if current_user.is_miraheze_verified:
        raise HTTPException(status_code=400, detail="已经绑定了Miraheze账户")

    if not current_user.miraheze_username or not current_user.miraheze_verify_code:
        raise HTTPException(status_code=400, detail="请先发起绑定申请")

    miraheze_username = current_user.miraheze_username
    verify_code = current_user.miraheze_verify_code
    page_title = f"User:{miraheze_username}/wikiio-verify"

    try:
        headers = {
            "User-Agent": "Wikiio/1.0 (Wiki data analysis platform; https://github.com/EilixiusLu/wikiio)"
        }
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            response = await client.get(
                "https://meta.miraheze.org/w/api.php",
                params={
                    "action": "query",
                    "titles": page_title,
                    "prop": "revisions",
                    "rvprop": "content",
                    "rvlimit": 1,
                    "format": "json",
                    "utf8": "1",
                }
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        logger.error("Miraheze API HTTP error: status=%s body=%s", e.response.status_code, e.response.text[:500])
        raise HTTPException(status_code=503, detail=f"Miraheze API 返回 HTTP {e.response.status_code}")
    except Exception as e:
        logger.error("Miraheze API connection error: %s", str(e))
        raise HTTPException(status_code=503, detail=f"无法连接到Miraheze API: {str(e)}")

    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))

    if "missing" in page:
        raise HTTPException(
            status_code=400,
            detail=f"找不到页面 {page_title}，请确认已在 Miraheze Meta 创建该页面"
        )

    revisions = page.get("revisions", [])
    if not revisions:
        raise HTTPException(status_code=400, detail="页面内容为空")

    page_content = revisions[0].get("*", "") or revisions[0].get("content", "")

    if verify_code not in page_content:
        raise HTTPException(
            status_code=400,
            detail="验证码不匹配，请确认已将验证码填入页面"
        )

    current_user.is_miraheze_verified = True
    current_user.miraheze_verify_code = None
    if current_user.role < 1:
        current_user.role = 1
    await db.commit()

    return {
        "message": "Miraheze账户绑定成功！",
        "miraheze_username": miraheze_username,
    }

@router.delete("/miraheze/unbind")
async def miraheze_unbind(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """解绑Miraheze账户"""
    current_user.miraheze_username = None
    current_user.miraheze_verify_code = None
    current_user.is_miraheze_verified = False
    await db.commit()
    return {"message": "已解绑Miraheze账户"}