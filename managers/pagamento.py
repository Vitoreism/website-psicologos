import logging
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from schemas.pagamento_schemas import (
    PagamentoResponse,
    FaturamentoPorMetodo,
    FaturamentoPorDia,
    FaturamentoPorMes,
    ResumoFinanceiro,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PagamentoManager:

    def __init__(self, engine: Engine, tabela: str = "pagamentos") -> None:
        self.engine = engine
        self.tabela = tabela
        logger.info("PagamentoManager criado.")

    # ─────────────────────────────────────────────────────────────
    # RESUMO FINANCEIRO GERAL (para o card de topo do dashboard)
    # ─────────────────────────────────────────────────────────────

    def resumo_financeiro(
        self,
        id_psicologo: int,
        inicio: datetime,
        fim: datetime,
    ) -> ResumoFinanceiro:
        """
        Retorna o total faturado no período + breakdown por método de pagamento.
        """
        query_total = text(f"""
            SELECT
                COALESCE(SUM(valor), 0)  AS total_faturado,
                COUNT(*)                  AS total_consultas
            FROM {self.tabela}
            WHERE id_psicologo = :id_psicologo
              AND data_pagamento >= :inicio
              AND data_pagamento <= :fim;
        """)

        query_por_metodo = text(f"""
            SELECT
                metodo_pagamento,
                COALESCE(SUM(valor), 0) AS total,
                COUNT(*)                 AS quantidade_consultas
            FROM {self.tabela}
            WHERE id_psicologo = :id_psicologo
              AND data_pagamento >= :inicio
              AND data_pagamento <= :fim
            GROUP BY metodo_pagamento
            ORDER BY total DESC;
        """)

        params = {"id_psicologo": id_psicologo, "inicio": inicio, "fim": fim}

        try:
            with self.engine.connect() as conn:
                row_total = conn.execute(query_total, params).mappings().first()
                rows_metodo = conn.execute(query_por_metodo, params).mappings().all()

            por_metodo = [FaturamentoPorMetodo(**row) for row in rows_metodo]

            return ResumoFinanceiro(
                periodo_inicio=inicio,
                periodo_fim=fim,
                total_faturado=row_total["total_faturado"],
                total_consultas=row_total["total_consultas"],
                por_metodo=por_metodo,
            )

        except Exception as e:
            logger.error(f"Erro ao gerar resumo financeiro: {e}", exc_info=True)
            return ResumoFinanceiro(
                periodo_inicio=inicio,
                periodo_fim=fim,
                total_faturado=Decimal("0"),
                total_consultas=0,
                por_metodo=[],
            )

    # ─────────────────────────────────────────────────────────────
    # FATURAMENTO DIÁRIO (gráfico de linha/barra por dia)
    # ─────────────────────────────────────────────────────────────

    def faturamento_por_dia(
        self,
        id_psicologo: int,
        inicio: datetime,
        fim: datetime,
    ) -> List[FaturamentoPorDia]:
        """
        Retorna o faturamento agrupado por dia.
        Ideal para gráficos de linha mostrando evolução diária.
        """
        query = text(f"""
            SELECT
                TO_CHAR(data_pagamento AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD') AS dia,
                COALESCE(SUM(valor), 0) AS total,
                COUNT(*)                 AS quantidade_consultas
            FROM {self.tabela}
            WHERE id_psicologo = :id_psicologo
              AND data_pagamento >= :inicio
              AND data_pagamento <= :fim
            GROUP BY dia
            ORDER BY dia ASC;
        """)

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(query, {"id_psicologo": id_psicologo, "inicio": inicio, "fim": fim}).mappings().all()

            logger.info(f"Faturamento diário: {len(rows)} dias encontrados para psicólogo {id_psicologo}.")
            return [FaturamentoPorDia(**row) for row in rows]

        except Exception as e:
            logger.error(f"Erro ao buscar faturamento por dia: {e}", exc_info=True)
            return []

    # ─────────────────────────────────────────────────────────────
    # FATURAMENTO MENSAL (gráfico de visão geral anual)
    # ─────────────────────────────────────────────────────────────

    def faturamento_por_mes(
        self,
        id_psicologo: int,
        ano: int,
    ) -> List[FaturamentoPorMes]:
        """
        Retorna o faturamento mês a mês de um ano inteiro.
        Ideal para o gráfico de barras de visão anual.
        """
        query = text(f"""
            SELECT
                TO_CHAR(data_pagamento AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM') AS mes,
                COALESCE(SUM(valor), 0) AS total,
                COUNT(*)                 AS quantidade_consultas
            FROM {self.tabela}
            WHERE id_psicologo = :id_psicologo
              AND EXTRACT(YEAR FROM data_pagamento AT TIME ZONE 'America/Sao_Paulo') = :ano
            GROUP BY mes
            ORDER BY mes ASC;
        """)

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(query, {"id_psicologo": id_psicologo, "ano": ano}).mappings().all()

            logger.info(f"Faturamento mensal ({ano}): {len(rows)} meses para psicólogo {id_psicologo}.")
            return [FaturamentoPorMes(**row) for row in rows]

        except Exception as e:
            logger.error(f"Erro ao buscar faturamento por mês: {e}", exc_info=True)
            return []

    # ─────────────────────────────────────────────────────────────
    # FATURAMENTO POR MÉTODO (breakdown para gráfico de pizza)
    # ─────────────────────────────────────────────────────────────

    def faturamento_por_metodo(
        self,
        id_psicologo: int,
        inicio: datetime,
        fim: datetime,
    ) -> List[FaturamentoPorMetodo]:
        """
        Retorna o faturamento agrupado por método de pagamento.
        Ideal para gráficos de pizza ou barras horizontais.
        """
        query = text(f"""
            SELECT
                metodo_pagamento,
                COALESCE(SUM(valor), 0) AS total,
                COUNT(*)                 AS quantidade_consultas
            FROM {self.tabela}
            WHERE id_psicologo = :id_psicologo
              AND data_pagamento >= :inicio
              AND data_pagamento <= :fim
            GROUP BY metodo_pagamento
            ORDER BY total DESC;
        """)

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(query, {"id_psicologo": id_psicologo, "inicio": inicio, "fim": fim}).mappings().all()

            logger.info(f"Faturamento por método: {len(rows)} métodos para psicólogo {id_psicologo}.")
            return [FaturamentoPorMetodo(**row) for row in rows]

        except Exception as e:
            logger.error(f"Erro ao buscar faturamento por método: {e}", exc_info=True)
            return []
