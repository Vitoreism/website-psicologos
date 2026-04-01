from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


class PagamentoCreate(BaseModel):
    """
    Dados para criação de um pagamento (uso interno pelo ConsultaManager).
    """
    id_psicologo: int
    id_paciente: int
    valor: Decimal = Field(gt=0, description="Valor pago")
    metodo_pagamento: str = Field(min_length=2, max_length=30)


class PagamentoResponse(BaseModel):
    """
    Retorno completo de um pagamento.
    """
    id_pagamento: int
    id_psicologo: int
    id_paciente: int
    valor: Decimal
    metodo_pagamento: str
    data_pagamento: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ─────────────────────────────────────────────
# Schemas para análise financeira / dashboard
# ─────────────────────────────────────────────

class FaturamentoPorMetodo(BaseModel):
    """
    Faturamento agrupado por método de pagamento em um período.
    """
    metodo_pagamento: str
    total: Decimal
    quantidade_consultas: int

    model_config = ConfigDict(from_attributes=True)


class ResumoFinanceiro(BaseModel):
    """
    Resumo financeiro para um período (dia / semana / mês / intervalo customizado).
    """
    periodo_inicio: datetime
    periodo_fim: datetime
    total_faturado: Decimal
    total_consultas: int
    por_metodo: List[FaturamentoPorMetodo]

    model_config = ConfigDict(from_attributes=True)


class FaturamentoPorDia(BaseModel):
    """
    Faturamento diário — ideal para gráficos de linha/barra.
    """
    dia: str        # formato "YYYY-MM-DD"
    total: Decimal
    quantidade_consultas: int

    model_config = ConfigDict(from_attributes=True)


class FaturamentoPorMes(BaseModel):
    """
    Faturamento mensal — ideal para gráficos de visão geral anual.
    """
    mes: str        # formato "YYYY-MM"
    total: Decimal
    quantidade_consultas: int

    model_config = ConfigDict(from_attributes=True)
