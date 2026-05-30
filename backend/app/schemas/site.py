from pydantic import BaseModel, field_validator
from typing import Optional


class SiteCreate(BaseModel):
    name: str
    site_id: str
    base_url: str
    platform: str = "fandom"
    has_ratepage: bool = False
    description: str = ""
    language: str = "zh"

    @field_validator("platform")
    @classmethod
    def platform_valid(cls, v):
        if v not in ("fandom", "miraheze"):
            raise ValueError("平台类型必须是 fandom 或 miraheze")
        return v

    @field_validator("site_id")
    @classmethod
    def site_id_valid(cls, v):
        if not v.strip():
            raise ValueError("站点编号不能为空")
        return v.strip()
