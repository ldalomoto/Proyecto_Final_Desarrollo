from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class CareerResponse(BaseModel):
    id: UUID
    nombre: str
    area: Optional[str]
    imagen: Optional[str]
    descripcion: Optional[str]
    duracion: Optional[str]
    modalidad: Optional[str]
    salarioPromedio: Optional[str]
    universidades: List[str]
    url: Optional[str]
