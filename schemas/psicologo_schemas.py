from pydantic import BaseModel, EmailStr, Field, ConfigDict

class PsicologoBase(BaseModel):
    crp: str = Field(..., min_length=4, description="Registro no Conselho Regional de Psicologia (Identificador unico por psicologo)")
    primeiro_nome: str = Field(..., min_length=2, description="Primeiro nome do psicólogo")
    ultimo_nome: str = Field(..., min_length=2, description="Último nome ou sobrenome do psicólogo")
    email: EmailStr = Field(..., description="E-mail válido para contato e login")

class PsicologoCreate(PsicologoBase):
    senha: str = Field(..., min_length=6, description="Senha em texto plano")