"""
插件相关配置
"""

from typing import Dict
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    update_time: int = 720  # 更新时间间隔 [分钟]
    # proxies: str = ""