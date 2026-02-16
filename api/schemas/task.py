from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    id_task: int
    creador: str
    descripcion: str
    fecha_creacion: datetime