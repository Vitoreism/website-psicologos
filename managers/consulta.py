import logging
from decimal import Decimal
from typing import List, Optional, Union
from datetime import datetime, date

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from schemas.consulta_schemas import ConsultaCreate, ConsultaResponse, ConsultaResumo
from schemas.pagamento_schemas import PagamentoCreate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ConsultaManager:

    def __init__(self, engine: Engine, tabela_consultas: str = "consultas", tabela_pagamentos: str = "pagamentos") -> None:
        self.engine = engine
        self.tabela_consultas = tabela_consultas
        self.tabela_pagamentos = tabela_pagamentos
        logger.info("ConsultaManager criado.")

    # ─────────────────────────────────────────────────────────────
    # CRIAÇÃO — consulta + pagamento em uma única transação atômica
    # ─────────────────────────────────────────────────────────────

    def criar_consulta_com_pagamento(
        self,
        consulta: ConsultaCreate,
        id_psicologo: int
    ) -> ConsultaResponse | None:
        """
        Cria um pagamento e a consulta vinculada em uma única transação.
        Se qualquer uma das operações falhar, nenhuma é persistida.
        """

        insert_pagamento = text(f"""
            INSERT INTO {self.tabela_pagamentos} (id_psicologo, id_paciente, valor, metodo_pagamento)
            VALUES (:id_psicologo, :id_paciente, :valor, :metodo_pagamento)
            RETURNING id_pagamento, data_pagamento;
        """)

        insert_consulta = text(f"""
            INSERT INTO {self.tabela_consultas} (id_psicologo, id_paciente, id_pagamento, dia, horario_inicio, horario_fim)
            VALUES (:id_psicologo, :id_paciente, :id_pagamento, :dia, :horario_inicio, :horario_fim)
            RETURNING id_consulta, criado_em;
        """)

        try:
            with self.engine.begin() as conn:   # begin() faz commit automático ou rollback em caso de erro
                # 1. Inserir pagamento
                pagamento_result = conn.execute(insert_pagamento, {
                    "id_psicologo": id_psicologo,
                    "id_paciente": consulta.id_paciente,
                    "valor": consulta.valor,
                    "metodo_pagamento": consulta.metodo_pagamento,
                })
                pagamento_row = pagamento_result.mappings().first()
                id_pagamento = pagamento_row["id_pagamento"]
                data_pagamento = pagamento_row["data_pagamento"]

                # 2. Inserir consulta com o id_pagamento recém-criado
                consulta_result = conn.execute(insert_consulta, {
                    "id_psicologo": id_psicologo,
                    "id_paciente": consulta.id_paciente,
                    "id_pagamento": id_pagamento,
                    "dia": consulta.dia,
                    "horario_inicio": consulta.horario_inicio,
                    "horario_fim": consulta.horario_fim,
                })
                consulta_row = consulta_result.mappings().first()
                id_consulta = consulta_row["id_consulta"]
                criado_em = consulta_row["criado_em"]

            logger.info(f"Consulta {id_consulta} criada com pagamento {id_pagamento} para psicólogo {id_psicologo}.")

            return ConsultaResponse(
                id_consulta=id_consulta,
                id_psicologo=id_psicologo,
                id_paciente=consulta.id_paciente,
                id_pagamento=id_pagamento,
                dia=consulta.dia,
                horario_inicio=consulta.horario_inicio,
                horario_fim=consulta.horario_fim,
                criado_em=criado_em,
                valor=consulta.valor,
                metodo_pagamento=consulta.metodo_pagamento,
                data_pagamento=data_pagamento,
            )

        except IntegrityError as e:
            logger.warning(f"Erro de integridade ao criar consulta (paciente/psicólogo inválido?): {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar consulta com pagamento: {e}", exc_info=True)
            return None

    # ─────────────────────────────────────────────────────────────
    # LEITURA
    # ─────────────────────────────────────────────────────────────

    def listar_consultas(
        self,
        id_psicologo: int,
        id_paciente: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> List[ConsultaResumo]:
        """
        Lista consultas do psicólogo com JOIN no paciente e pagamento.
        Suporta filtros opcionais por paciente e intervalo de data.
        """
        filtros = ["c.id_psicologo = :id_psicologo"]
        params: dict = {"id_psicologo": id_psicologo}

        if id_paciente:
            filtros.append("c.id_paciente = :id_paciente")
            params["id_paciente"] = id_paciente

        if data_inicio:
            filtros.append("c.dia >= :data_inicio")
            params["data_inicio"] = data_inicio

        if data_fim:
            filtros.append("c.dia <= :data_fim")
            params["data_fim"] = data_fim

        where_clause = " AND ".join(filtros)

        query = text(f"""
            SELECT
                c.id_consulta,
                c.id_paciente,
                c.dia,
                c.horario_inicio,
                c.horario_fim,
                (pac.primeiro_nome || ' ' || pac.ultimo_nome) AS nome_paciente,
                pag.valor,
                pag.metodo_pagamento
            FROM {self.tabela_consultas} c
            LEFT JOIN pacientes pac ON pac.id_paciente = c.id_paciente
            LEFT JOIN {self.tabela_pagamentos} pag ON pag.id_pagamento = c.id_pagamento
            WHERE {where_clause}
            ORDER BY c.dia DESC, c.horario_inicio DESC;
        """)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                rows = result.mappings().all()

            logger.info(f"Listagem de consultas para psicólogo {id_psicologo}: {len(rows)} encontradas.")
            return [ConsultaResumo(**row) for row in rows]

        except Exception as e:
            logger.error(f"Erro ao listar consultas: {e}", exc_info=True)
            return []

    def buscar_consulta_por_id(self, id_consulta: int, id_psicologo: int) -> Optional[ConsultaResponse]:
        """
        Retorna os detalhes completos de uma única consulta.
        """
        query = text(f"""
            SELECT
                c.id_consulta,
                c.id_psicologo,
                c.id_paciente,
                c.id_pagamento,
                c.dia,
                c.horario_inicio,
                c.horario_fim,
                c.criado_em,
                (pac.primeiro_nome || ' ' || pac.ultimo_nome) AS nome_paciente,
                pag.valor,
                pag.metodo_pagamento,
                pag.data_pagamento
            FROM {self.tabela_consultas} c
            LEFT JOIN pacientes pac ON pac.id_paciente = c.id_paciente
            LEFT JOIN {self.tabela_pagamentos} pag ON pag.id_pagamento = c.id_pagamento
            WHERE c.id_consulta = :id_consulta AND c.id_psicologo = :id_psicologo;
        """)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id_consulta": id_consulta, "id_psicologo": id_psicologo})
                row = result.mappings().first()

            if row is None:
                logger.warning(f"Consulta {id_consulta} não encontrada para psicólogo {id_psicologo}.")
                return None

            return ConsultaResponse(**row)

        except Exception as e:
            logger.error(f"Erro ao buscar consulta {id_consulta}: {e}", exc_info=True)
            return None

    # ─────────────────────────────────────────────────────────────
    # DELEÇÃO
    # ─────────────────────────────────────────────────────────────

    def deletar_consulta(self, id_consulta: int, id_psicologo: int) -> bool:
        """
        Remove uma consulta do banco de dados.
        O pagamento vinculado permanece por razões de auditoria financeira
        (FK definida como ON DELETE SET NULL na tabela consultas).
        """
        query = text(f"""
            DELETE FROM {self.tabela_consultas}
            WHERE id_consulta = :id_consulta AND id_psicologo = :id_psicologo;
        """)

        try:
            with self.engine.begin() as conn:
                result = conn.execute(query, {"id_consulta": id_consulta, "id_psicologo": id_psicologo})

            if result.rowcount > 0:
                logger.info(f"Consulta {id_consulta} deletada para psicólogo {id_psicologo}.")
                return True
            else:
                logger.warning(f"Consulta {id_consulta} não encontrada ou pertence a outro psicólogo.")
                return False

        except Exception as e:
            logger.error(f"Erro ao deletar consulta {id_consulta}: {e}", exc_info=True)
            return False

    
    def get_quantidade_consultas_hoje(self, id_psicologo: int) -> int:
        """
        Retorna apenas a quantidade de consultas do dia atual via um COUNT otimizado.
        """
        query = text(f"""
            SELECT COUNT(c.id_consulta) AS quantidade
            FROM {self.tabela_consultas} c
            WHERE c.id_psicologo = :id_psicologo
              AND c.dia = CURRENT_DATE;
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id_psicologo": id_psicologo})
                row = result.mappings().first()
                if row:
                    return row["quantidade"]
                return 0
        except Exception as e:
            logger.error(f"Erro ao buscar quantidade de consultas hoje: {e}", exc_info=True)
            return 0

    def get_consultas_hoje(self, id_psicologo: int) -> List[ConsultaResumo]:
        """
        Retorna as consultas agendadas para o dia atual.
        """
        hoje = date.today()
        return self.listar_consultas(id_psicologo=id_psicologo, data_inicio=hoje, data_fim=hoje)