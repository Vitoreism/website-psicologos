from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from utils.validators import validar_senha


class PsicologoBase(BaseModel):
    crp: str = Field(min_length=4, description="Registro no Conselho Regional de Psicologia (Identificador unico por psicologo)")
    primeiro_nome: str = Field(min_length=2, description="Primeiro nome do psicólogo")
    ultimo_nome: str = Field(min_length=2, description="Último nome ou sobrenome do psicólogo")
    email: EmailStr = Field(description="E-mail válido para contato e login")

class PsicologoCreate(PsicologoBase):
    senha: str = Field(min_length=8, description="Senha em texto plano")

    @field_validator('senha')
    @classmethod
    def validar_regras_senha(cls, valor_da_senha: str): 
        senha_valida, mensagem_erro = validar_senha(valor_da_senha)
        
        if not senha_valida:
            raise ValueError(mensagem_erro)
            
        return valor_da_senha

class PsicologoUpdate(BaseModel):
    primeiro_nome: Optional[str] = None
    ultimo_nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None


class PsicologoResponse(PsicologoBase):
    ...
    id: int 
    model_config = ConfigDict(from_attributes=True)