from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional 

class PacienteBase(BaseModel):
    primeiro_nome: str = Field(min_length=2, max_length=50)
    ultimo_nome: str = Field(min_length=2, max_length=50)
    email: EmailStr


class PacienteCreate(PacienteBase):
    pass


class PacienteResponse(PacienteBase):
    id: int = Field(validation_alias="id_paciente")
    id_psicologo: int
    is_ativo: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PacienteUpdate(BaseModel):
    primeiro_nome: Optional[str] = Field(None, min_length=2, max_length=50)
    ultimo_nome: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    is_ativo: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)