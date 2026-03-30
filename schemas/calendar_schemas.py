from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime 
import pytz 


class CalendarQueryRequest(BaseModel):
    inicio: datetime = Field(description="Horário de início de uma atividade") # Já contém o dia a hora em si
    fim: datetime = Field(description="Horário do fim de uma atividade")  # Já contém o dia e a hora em si 

    @field_validator('fim')
    @classmethod
    def validar_intervalo(cls, v, info):
        inicio = info.data.get('inicio')

        if inicio and v <= inicio:
            raise ValueError("O horário de fim deve ser posterior ao horário de início.")
    
        return v 


class CreateEventRequest(BaseModel):
    titulo: str = Field(description="Título do evento / consulta")
    inicio: datetime = Field(description="Horário de início do evento")
    fim: datetime = Field(description="Horário de fim do evento")
    descricao: str | None = Field(default=None, description="Descrição ou observações sobre o evento")
    fuso_horario: str = Field(default="America/Sao_Paulo", description="Fuso horário do evento (padrão: Brazil/Brasília)")

    @field_validator('fim')
    @classmethod
    def validar_intervalo(cls, v, info):
        inicio = info.data.get('inicio')
        if inicio and v <= inicio:
            raise ValueError("O horário de fim deve ser posterior ao horário de início.")
        return v

