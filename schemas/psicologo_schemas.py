from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class PsicologoBase(BaseModel):
    crp: str = Field(min_length=4, description="Registro no Conselho Regional de Psicologia (Identificador unico por psicologo)")
    primeiro_nome: str = Field(min_length=2, description="Primeiro nome do psicólogo")
    ultimo_nome: str = Field(min_length=2, description="Último nome ou sobrenome do psicólogo")
    email: EmailStr = Field(description="E-mail válido para contato e login")

class PsicologoCreate(PsicologoBase):
    senha: str = Field(min_length=6, description="Senha em texto plano")


class PsicologoUpdate(BaseModel):
    primeiro_nome: Optional[str] = None
    ultimo_nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None


class PsicologoResponse(PsicologoBase):
    ...
    id: int 
    model_config = ConfigDict(from_attributes=True)