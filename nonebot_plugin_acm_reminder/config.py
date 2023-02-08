"""
插件相关配置
"""

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    update_time: int = 360