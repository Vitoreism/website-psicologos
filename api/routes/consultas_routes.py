from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, date
from typing import Optional, List

from data.database import connect_db
from managers.consulta import ConsultaManager
from managers.pagamento import PagamentoManager
from utils.auth import get_current_psicologo
from schemas.consulta_schemas import ConsultaResponse, ConsultaResumo
from schemas.pagamento_schemas import ResumoFinanceiro, FaturamentoPorDia, FaturamentoPorMes, FaturamentoPorMetodo

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_consulta_manager():
    engine = connect_db()
    return ConsultaManager(engine=engine)


def get_pagamento_manager():
    engine = connect_db()
    return PagamentoManager(engine=engine)


# ─────────────────────────────────────────────────────────────
# CONSULTAS
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[ConsultaResumo], summary="Listar consultas do psicólogo")
def listar_consultas(
    id_paciente: Optional[int] = Query(None, description="Filtrar por paciente específico"),
    data_inicio: Optional[date] = Query(None, description="Filtrar a partir desta data (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Filtrar até esta data (YYYY-MM-DD)"),
    manager: ConsultaManager = Depends(get_consulta_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna todas as consultas do psicólogo autenticado.
    Suporta filtros opcionais por paciente e intervalo de datas.
    """
    return manager.listar_consultas(
        id_psicologo=psicologo_id,
        id_paciente=id_paciente,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/{id_consulta}", response_model=ConsultaResponse, summary="Buscar consulta por ID")
def buscar_consulta(
    id_consulta: int,
    manager: ConsultaManager = Depends(get_consulta_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna os detalhes completos de uma consulta específica, incluindo dados do pagamento.
    """
    consulta = manager.buscar_consulta_por_id(id_consulta=id_consulta, id_psicologo=psicologo_id)
    if consulta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta {id_consulta} não encontrada."
        )
    return consulta


@router.delete("/{id_consulta}", summary="Deletar consulta")
def deletar_consulta(
    id_consulta: int,
    manager: ConsultaManager = Depends(get_consulta_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Remove uma consulta. O pagamento vinculado é preservado para fins de auditoria.
    """
    sucesso = manager.deletar_consulta(id_consulta=id_consulta, id_psicologo=psicologo_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consulta {id_consulta} não encontrada ou não pertence a este psicólogo."
        )
    return {"mensagem": f"Consulta {id_consulta} removida com sucesso."}


# ─────────────────────────────────────────────────────────────
# FINANCEIRO / DASHBOARD
# ─────────────────────────────────────────────────────────────

@router.get(
    "/financeiro/resumo",
    response_model=ResumoFinanceiro,
    summary="Resumo financeiro por período",
)
def resumo_financeiro(
    inicio: datetime = Query(description="Início do período (ISO 8601), ex: 2026-03-01T00:00:00"),
    fim: datetime = Query(description="Fim do período (ISO 8601), ex: 2026-03-31T23:59:59"),
    manager: PagamentoManager = Depends(get_pagamento_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna o total faturado no período e o detalhamento por método de pagamento.
    Ideal para o card de faturamento total e gráfico de pizza no dashboard.
    """
    return manager.resumo_financeiro(id_psicologo=psicologo_id, inicio=inicio, fim=fim)


@router.get(
    "/financeiro/por-dia",
    response_model=List[FaturamentoPorDia],
    summary="Faturamento diário",
)
def faturamento_por_dia(
    inicio: datetime = Query(description="Início do período (ISO 8601)"),
    fim: datetime = Query(description="Fim do período (ISO 8601)"),
    manager: PagamentoManager = Depends(get_pagamento_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna o faturamento agrupado por dia dentro do período informado.
    Ideal para gráficos de linha ou barra com evolução diária.
    """
    return manager.faturamento_por_dia(id_psicologo=psicologo_id, inicio=inicio, fim=fim)


@router.get(
    "/financeiro/por-mes",
    response_model=List[FaturamentoPorMes],
    summary="Faturamento mensal do ano",
)
def faturamento_por_mes(
    ano: int = Query(default=datetime.now().year, description="Ano a consultar, ex: 2026"),
    manager: PagamentoManager = Depends(get_pagamento_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna o faturamento mês a mês de um ano inteiro.
    Ideal para o gráfico de barras de visão anual no dashboard.
    """
    return manager.faturamento_por_mes(id_psicologo=psicologo_id, ano=ano)


@router.get(
    "/financeiro/por-metodo",
    response_model=List[FaturamentoPorMetodo],
    summary="Faturamento por método de pagamento",
)
def faturamento_por_metodo(
    inicio: datetime = Query(description="Início do período (ISO 8601)"),
    fim: datetime = Query(description="Fim do período (ISO 8601)"),
    manager: PagamentoManager = Depends(get_pagamento_manager),
    psicologo_id: int = Depends(get_current_psicologo),
):
    """
    Retorna o faturamento detalhado por categoria/tipo de pagamento no período.
    Ideal para gráfico de pizza ou barras horizontais no dashboard financeiro.
    """
    return manager.faturamento_por_metodo(id_psicologo=psicologo_id, inicio=inicio, fim=fim)
