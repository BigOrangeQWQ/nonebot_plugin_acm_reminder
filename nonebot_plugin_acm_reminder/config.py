"""
插件相关配置
"""

from pydantic import BaseModel


class Config(BaseModel):
    update_time: int = 720  # 更新时间间隔 [分钟]
    # proxies: str = ""