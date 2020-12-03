from pydantic import BaseModel
from datetime import datetime

class Datasets(BaseModel):
    object_id: str
    type: str
    dataset: str
    name: str
    bundle: str
    version: str
    description: str = None
    mime_type: str = None
    created_time: datetime
    aliases: str = None