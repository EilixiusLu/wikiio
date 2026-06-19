"""
Resend 邮件发送工具
"""

import asyncio
from functools import partial

import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


def _build_verification_url(token: str) -> str:
    """拼接前端验证链接，兼容 Hash History 路由"""
    return f"{settings.FRONTEND_BASE_URL}/#/verify-email?token={token}"


async def send_verification_email(to_email: str, username: str, token: str) -> None:
    """
    发送邮箱验证邮件。
    Resend SDK 为同步接口，通过 run_in_executor 在异步上下文中调用。
    """
    verify_url = _build_verification_url(token)

    html_content = f"""\
<div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
  <h2 style="color: #185897; margin-bottom: 8px;">欢迎加入 Wikiio</h2>
  <p style="color: #444; line-height: 1.6;">你好 <strong>{username}</strong>，</p>
  <p style="color: #444; line-height: 1.6;">
    请点击下方按钮验证你的邮箱地址，链接有效期为 <strong>24 小时</strong>。
  </p>
  <a href="{verify_url}"
     style="display:inline-block; margin: 24px 0; padding: 12px 28px;
            background-color: #185897; color: #fff; text-decoration: none;
            border-radius: 6px; font-size: 15px;">
    验证邮箱
  </a>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">
    如果按钮无法点击，请复制以下链接到浏览器：<br>
    <a href="{verify_url}" style="color: #185897; word-break: break-all;">{verify_url}</a>
  </p>
  <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
  <p style="color: #aaa; font-size: 12px;">
    如果你没有注册 Wikiio 账户，请忽略此邮件。
  </p>
</div>"""

    send_fn = partial(
        resend.Emails.send,
        {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "验证你的 Wikiio 邮箱",
            "html": html_content,
        },
    )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, send_fn)


async def send_verification_resend_email(to_email: str, username: str, token: str) -> None:
    """重发验证邮件（与 send_verification_email 逻辑相同，语义区分）"""
    await send_verification_email(to_email, username, token)
