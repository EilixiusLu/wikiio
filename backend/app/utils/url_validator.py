"""
URL 安全校验工具：防止 SSRF 攻击

对所有用户提交的 base_url 进行严格的域名白名单校验，
确保爬虫引擎只能向合法的 Fandom / Miraheze 维基发起请求。
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional


# ── 允许的域名后缀（白名单） ──
ALLOWED_DOMAIN_SUFFIXES = (
    ".fandom.com",
    ".miraheze.org",
    ".wikia.org",       # 部分旧 Fandom 域的别名
    ".gamepedia.com",   # Fandom 托管的游戏 Wiki
)

# ── 私有 IP 段 ──
PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),       # 多播
    ipaddress.ip_network("240.0.0.0/4"),       # 保留
    ipaddress.ip_network("0.0.0.0/8"),         # 当前网络
    ipaddress.ip_network("100.64.0.0/10"),     # CGNAT
    ipaddress.ip_network("198.18.0.0/15"),     # 基准测试
    ipaddress.ip_network("::1/128"),           # IPv6 环回
    ipaddress.ip_network("fc00::/7"),          # IPv6 唯一本地
    ipaddress.ip_network("fe80::/10"),         # IPv6 链路本地
    ipaddress.ip_network("::ffff:0:0/96"),     # IPv4 映射的 IPv6
]


def is_private_ip(hostname: str) -> bool:
    """检查主机名是否解析到私有/保留 IP 地址"""
    try:
        # 先尝试直接解析为 IP 地址
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            # DNS 解析
            addr = ipaddress.ip_address(socket.getaddrinfo(hostname, None)[0][4][0])
        except (socket.gaierror, OSError, IndexError):
            return True  # 无法解析 → 拒绝

    for net in PRIVATE_NETWORKS:
        if addr in net:
            return True
    return False


def validate_base_url(url: str) -> str:
    """
    校验用户提交的 base_url 是否安全。

    规则:
    1. Scheme 必须为 https
    2. 主机名必须以允许的域名后缀结尾
    3. 主机名不得解析到私有/保留 IP
    4. URL 不得包含内嵌的认证信息 (@host)
    5. 端口必须为 443 或未指定

    返回: 标准化后的 base_url（去除尾部斜杠）

    Raises:
        ValueError: URL 未通过安全校验
    """
    # ── 基本解析 ──
    try:
        parsed = urlparse(url.strip())
    except Exception:
        raise ValueError("无法解析 URL")

    # 1. Scheme 检查
    if parsed.scheme != "https":
        raise ValueError(f"仅允许 https 协议，收到: {parsed.scheme}")

    # 2. 主机名存在性
    if not parsed.hostname:
        raise ValueError("URL 缺少有效主机名")

    hostname = parsed.hostname.lower()

    # 3. 禁止 IP 地址形式的 URL（如 https://127.0.0.1/）
    try:
        ipaddress.ip_address(hostname)
        raise ValueError("不允许使用 IP 地址作为主机名")
    except ValueError:
        pass  # 不是 IP 地址，继续

    # 4. 域名白名单
    if not hostname.endswith(ALLOWED_DOMAIN_SUFFIXES):
        raise ValueError(
            f"主机名 {hostname} 不在允许的域名范围内。"
            f"仅允许: {', '.join(ALLOWED_DOMAIN_SUFFIXES)}"
        )

    # 5. 禁止内嵌认证信息（如 https://user:pass@evil.com@legit.fandom.com/）
    if "@" in parsed.netloc.split("@")[-2:]:
        # 检查是否有多个 @ 符号（URL 混淆攻击）
        raise ValueError("URL 包含非法的认证信息")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL 不得包含认证信息")

    # 6. 端口检查
    if parsed.port is not None and parsed.port != 443:
        raise ValueError(f"仅允许 443 端口，收到: {parsed.port}")

    # 7. DNS 重绑定防护 — 解析后检查是否为私有 IP
    if is_private_ip(hostname):
        raise ValueError(f"主机名 {hostname} 解析到私有/保留 IP，拒绝连接")

    # 标准化返回: 去除尾部斜杠，保持小写主机名
    normalized = f"https://{hostname}{parsed.path.rstrip('/') if parsed.path != '/' else ''}"
    return normalized


def validate_api_url(api_url: str) -> str:
    """
    对已构造的 api_url 进行防御性校验（深度防御）。
    规则与 validate_base_url 一致，额外检查路径必须以 /api.php 或 /w/api.php 结尾。
    """
    try:
        parsed = urlparse(api_url.strip())
    except Exception:
        raise ValueError("无法解析 API URL")

    if parsed.scheme != "https":
        raise ValueError(f"API URL 必须使用 https: {api_url}")
    if not parsed.hostname:
        raise ValueError("API URL 缺少有效主机名")

    hostname = parsed.hostname.lower()
    if not hostname.endswith(ALLOWED_DOMAIN_SUFFIXES):
        raise ValueError(f"API URL 主机名不在白名单: {hostname}")
    if is_private_ip(hostname):
        raise ValueError(f"API URL 主机名解析到私有 IP: {hostname}")

    # 路径检查: 必须是指定的 API 端点
    if not (parsed.path.endswith("/api.php") or parsed.path.endswith("/w/api.php")):
        raise ValueError(f"API URL 路径必须以 /api.php 或 /w/api.php 结尾: {parsed.path}")

    return api_url
