import logging 
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from typing import Any, Dict, List
from data.database import connect_db
from utils.security import Security
from schemas.psicologo_schemas import PsicologoBase, PsicologoCreate, PsicologoUpdate, PsicologoResponse



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PsicologoManager:

    def __init__(self, engine: Engine, tabela: str) -> None:
        self.engine = engine 
        self.tabela = tabela

        logger.info("Psicologo Manager object created")

    def criar_psicologo(self, psicologo: PsicologoCreate) -> PsicologoResponse | None:
        senha_hash = Security.hash_password(psicologo.senha)

        query = text(f"""
        INSERT INTO {self.tabela} (primeiro_nome, ultimo_nome, crp, email, senha_hash)
        VALUES (:primeiro_nome, :ultimo_nome, :crp, :email, :senha_hash)
        RETURNING id, primeiro_nome, ultimo_nome, email, crp;
        """
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "primeiro_nome": psicologo.primeiro_nome,
                    "ultimo_nome": psicologo.ultimo_nome,
                    "crp": psicologo.crp,
                    "email": psicologo.email,
                    "senha_hash": senha_hash
                })
                conn.commit()
                psicologo_criado = result.mappings().first()

                logger.info("New psicologo added")
                return psicologo_criado
        except IntegrityError as e:
            logger.warning(f"Violação de unicidade ao criar psicólogo (email ou CRP duplicado): {e}")
            raise
        except Exception as e:
            logger.error(f"Error in creating new psicologo: {e}")
            return None


    def read_psicologos(self) -> List[PsicologoResponse]:
        query = text(f"SELECT id, primeiro_nome, ultimo_nome, crp, email FROM {self.tabela}")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                data = result.mappings().all()
            
            logger.info("Select made with succes")
            psicologos_seguros = [PsicologoResponse(**row) for row in data]
            return psicologos_seguros
        except Exception as e:
            logger.error(e)
            return []

    def gerar_relatorio(self) -> Dict[str, Any]:
        resumo_query = text(f"""
            SELECT
                COUNT(*) AS total_psicologos,
                COUNT(DISTINCT crp) AS total_crps_unicos,
                COUNT(DISTINCT email) AS total_emails_unicos,
                MIN(id) AS primeiro_id_cadastrado,
                MAX(id) AS ultimo_id_cadastrado
            FROM {self.tabela}
        """)
        dominios_query = text(f"""
            SELECT
                split_part(email, '@', 2) AS dominio_email,
                COUNT(*) AS quantidade
            FROM {self.tabela}
            GROUP BY dominio_email
            ORDER BY quantidade DESC, dominio_email ASC
        """)
        pacientes_query = text("SELECT COUNT(*) AS total_pacientes FROM pacientes")

        try:
            with self.engine.connect() as conn:
                resumo = conn.execute(resumo_query).mappings().one()
                dominios = conn.execute(dominios_query).mappings().all()

                total_pacientes = None
                try:
                    total_pacientes = conn.execute(pacientes_query).scalar()
                except Exception as exc:
                    logger.warning(f"Could not count pacientes table: {exc}")

            return {
                "resumo": dict(resumo),
                "dominios_email": [dict(row) for row in dominios],
                "total_pacientes": total_pacientes,
            }
        except Exception as e:
            logger.error(f"Error while generating report: {e}")
            return {
                "resumo": {
                    "total_psicologos": 0,
                    "total_crps_unicos": 0,
                    "total_emails_unicos": 0,
                    "primeiro_id_cadastrado": None,
                    "ultimo_id_cadastrado": None,
                },
                "dominios_email": [],
                "total_pacientes": None,
            }

    # Essa função depois vai ser quebrada em funcoes menores, para atualizar cada parte individual que se deseja
    def update_psicologo(self, crp: str, psicologo: PsicologoUpdate):
        """
        Detalhe -> Essa função irá atualizar o psicólogo de acordo com seu crp, e por motivos de boas práticas e legibilidade do código,
        esas função não irá permitir com que o crp seja alterado aqui
        """
        if psicologo.senha:
            senha_hash = Security.hash_password(psicologo.senha)
        campos_update = list()
        valores = {'crp_filter': str(crp)}


        try:
            if psicologo.primeiro_nome:
                campos_update.append("primeiro_nome = :primeiro_nome")
                valores["primeiro_nome"] = psicologo.primeiro_nome
        
            if psicologo.ultimo_nome:
                campos_update.append("ultimo_nome = :ultimo_nome")
                valores["ultimo_nome"] = psicologo.ultimo_nome

            if psicologo.email:
                campos_update.append("email = :email")
                valores["email"] = psicologo.email

            if psicologo.senha:
                campos_update.append("senha_hash = :senha_hash")
                valores['senha_hash'] = senha_hash

            if not campos_update:
                logger.warning("No fields to update")
                return None
            
            set_query = ", ".join(campos_update)
            
            query = text(f"UPDATE {self.tabela} SET {set_query} WHERE crp = :crp_filter")

            try:
                with self.engine.connect() as conn:
                    conn.execute(query, valores)
                    conn.commit()
                    logger.info("Psicologo table updated")
            
            except IntegrityError as e:
                logger.warning(f"Violação de unicidade ao atualizar psicólogo (email duplicado): {e}")
                raise
            except Exception as e:
                logger.error(f"Error while updationg psicologo table: {e}")
        except Exception as e:
            logger.error(f"Error in updating psicologo: {e}")

    
    def buscar_por_crp(self, crp: str) -> PsicologoResponse | None:
        query = text(
            f"SELECT id, primeiro_nome, ultimo_nome, crp, email FROM {self.tabela} WHERE crp = :crp"
        )
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"crp": str(crp)})
                row = result.mappings().first()
            if row is None:
                logger.warning(f"ERRO : Nenhum psicólogo encontrado com CRP {crp}.")
                return None
            return PsicologoResponse(**row)
        except Exception as e:
            logger.error(f"Erro ao buscar psicólogo com esse CRP: {e}")
            return None

    def delete_psicologo(self, crp: str) -> bool:
        query = text(f"DELETE FROM {self.tabela} WHERE crp = :crp_filter")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"crp_filter": str(crp)})
                conn.commit()

            if result.rowcount > 0:
                logger.info(f"Psicólogo com CRP {crp} deletado com sucesso.")
                return True
            else:
                logger.warning(f"Nenhum psicólogo encontrado com o CRP {crp}.")
                return False
                

        except Exception as e:
            logger.error(f"Erro ao deletar psicologo de crp {crp} : {e}")
            return False

if __name__ == "__main__":
    ps_manager = PsicologoManager(engine=connect_db(), tabela='psicologos')

    print("\n--- Teste de Criação Manual de Psicólogo ---")

    novo_ps = PsicologoCreate(
            primeiro_nome="Vasco",
            ultimo_nome="Da Gama",
            crp="1995024",
            email="vascocolina@gigante.com",
            senha="va4sc0"
        )

    #ps_manager.criar_psicologo(psicologo=novo_ps)


    lista_psicologos = ps_manager.read_psicologos()
    
    if lista_psicologos:
        print(f"{'ID':<5} | {'CRP':<10} | {'NOME COMPLETO':<30} | {'E-MAIL':<35}")
        print("-" * 95)

        for ps in lista_psicologos:
            nome_completo = f"{ps.primeiro_nome} {ps.ultimo_nome}"
            print(f"{ps.id:<5} | {ps.crp:<10} | {nome_completo:<30} | {ps.email:<35}")

        print("-" * 95)
        print(f"✅ Total de registros no banco: {len(lista_psicologos)}")
    else:
        print(f"{'NENHUM PSICÓLOGO ENCONTRADO NO BANCO DE DADOS':^95}")

    print("="*95 + "\n")    
