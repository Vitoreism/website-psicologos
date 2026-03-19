from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional 

class PacienteBase(BaseModel):
    primeiro_nome: str = Field(min_length=2, max_length=50)
    ultimo_nome: str = Field(min_length=2, max_length=50)
    email: EmailStr


class PacienteCreate(PacienteBase):
    senha: str = Field(min_length=6)


class PacienteResponse(PacienteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PacienteUpdate(BaseModel):
    primeiro_nome: Optional[str] = Field(None, min_length=2, max_length=50)
    ultimo_nome: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)