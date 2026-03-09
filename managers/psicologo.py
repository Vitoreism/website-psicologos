import logging 
from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Dict
from data.database import connect_db


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

    def criar_psicologo(self, primeiro_nome: str, ultimo_name: str, crp: str, email: str, senha: str) -> Dict:
        senha_hash = 'senhateste123'
        # Antes da query

        query = text(f"""
        INSERT INTO {self.tabela} (primeiro_nome, ultimo_nome, crp, email, senha_hash)
        VALUES (:primeiro_nome, :ultimo_nome, :crp, :email, :senha_hash)
        RETURNING id;
        """
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "primeiro_nome": primeiro_nome,
                    "ultimo_nome": ultimo_name,
                    "crp": crp,
                    "email": email,
                    "senha_hash": senha_hash
                })
                conn.commit()
                id = result.scalar()

                logger.info("New psicologo added")
                return id
        except Exception as e:
            logger.error(f"Error in creating new psicologo: {e}")
            return None


    def read_psicologos(self):
        query = text(f"SELECT * FROM {self.tabela}")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                dados = result.mappings().all()
            
            logger.info("Select made with succes")
            return dados
        except Exception as e:
            logger.error(e)


    def update_psicologo(self, crp: str, primeiro_nome: str = None, ultimo_nome: str = None, email: str = None, senha: str = None):
        """
        Detalhe -> Essa função irá atualizar o psicólogo de acordo com seu crp, e por motivos de boas práticas e legibilidade do código,
        esas função não irá permitir com que o crp seja alterado aqui
        """
        senha_hash = 'senhateste123'
        campos_update = list()
        valores = {'crp_filter': str(crp)}


        try:
            if primeiro_nome:
                campos_update.append("primeiro_nome = :primeiro_nome")
                valores["primeiro_nome"] = primeiro_nome
        
            if ultimo_nome:
                campos_update.append("ultimo_nome = :ultimo_nome")
                valores["ultimo_nome"] = ultimo_nome

            if email:
                campos_update.append("email = :email")
                valores["email"] = email

            if senha:
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
            
            except Exception as e:
                logger.error(f"Error while updationg psicologo table: {e}")
        except Exception as e:
            logger.error(f"Error in updating psicologo: {e}")

    
    def delete_psicologo(self, crp: str):
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
                

        except Exception as e:
            logger.error(f"Erro ao deletar psicologo de crp {crp} : {e}")

if __name__ == "__main__":
    ps_manager = PsicologoManager(engine=connect_db(), tabela='psicologos')
   # ps_manager.criar_psicologo(primeiro_nome='Vitor', ultimo_name='Machado', crp='2424248',email='vitor@gmail.com', senha='Genrolindo123')
    #print(ps_manager)
    ps_manager.update_psicologo(crp=2424248, primeiro_nome='Joana', ultimo_nome='Nogueira')
    #ps_manager.delete_psicologo(crp=2424248)
    psicologos = ps_manager.read_psicologos()
    print(psicologos)
