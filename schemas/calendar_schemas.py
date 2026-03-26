from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime 
import pytz 


class CalendarQueryRequest(BaseModel):
    email: EmailStr
    inicio: datetime = Field(description="Horário de início de uma atividade")
    fim: datetime = Field(description="Horário do fim de uma atividade")

    @field_validator('fim')
    @classmethod
    def validar_intervalo(cls, v, info):
        inicio = info.data.get('inicio')

        if inicio and v <= inicio:
            raise ValueError("O horário de fim deve ser posterior ao horário de início.")
    
        return v 
    
