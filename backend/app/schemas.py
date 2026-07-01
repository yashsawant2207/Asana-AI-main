from pydantic import BaseModel


class FrameConfig(BaseModel):
    type: str = "config"
    pose: str
