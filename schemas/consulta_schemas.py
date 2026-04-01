from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


class ConsultaCreate(BaseModel):
    """
    Dados necessários para agendar uma nova consulta.
    O pagamento é registrado simultaneamente e considerado pago no ato.
    """
    id_paciente: int = Field(description="ID do paciente vinculado ao psicólogo")
    dia: date = Field(description="Data da consulta (YYYY-MM-DD)")
    horario_inicio: datetime = Field(description="Data e hora de início da consulta (ISO 8601)")
    horario_fim: datetime = Field(description="Data e hora de fim da consulta (ISO 8601)")

    # Dados de pagamento — registrados no momento do agendamento
    valor: Decimal = Field(gt=0, description="Valor cobrado pela consulta")
    metodo_pagamento: str = Field(
        min_length=2,
        max_length=30,
        description="Método de pagamento: pix, cartao_credito, cartao_debito, dinheiro, transferencia"
    )

    @field_validator("horario_fim")
    @classmethod
    def validar_horarios(cls, v, info):
        inicio = info.data.get("horario_inicio")
        if inicio and v <= inicio:
            raise ValueError("O horário de fim deve ser posterior ao horário de início.")
        return v


class ConsultaResponse(BaseModel):
    """
    Resposta completa de uma consulta, incluindo dados do pagamento vinculado.
    """
    id_consulta: int
    id_psicologo: int
    id_paciente: int
    id_pagamento: Optional[int] = None

    dia: date
    horario_inicio: datetime
    horario_fim: datetime
    criado_em: datetime

    # Dados do paciente (JOIN)
    nome_paciente: Optional[str] = None

    # Dados do pagamento (JOIN)
    valor: Optional[Decimal] = None
    metodo_pagamento: Optional[str] = None
    data_pagamento: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ConsultaResumo(BaseModel):
    """
    Versão resumida da consulta para listagens.
    """
    id_consulta: int
    id_paciente: int
    nome_paciente: Optional[str] = None
    dia: date
    horario_inicio: datetime
    horario_fim: datetime
    valor: Optional[Decimal] = None
    metodo_pagamento: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
