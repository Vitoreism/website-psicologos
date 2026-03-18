import logging
import sys
from pathlib import Path
from typing import Tuple
from sqlalchemy import text
from faker import Faker  # pip install faker
from data.database import connect_db
import unicodedata

# Ajuste de Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.database import connect_db
from utils.security import Security # Usando sua criptografia real

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
fake = Faker('pt_BR') # Gera nomes e dados brasileiros

def limpar_banco(conn):
    """Limpa as tabelas para a apresentação."""
    logger.info("Limpando tabelas de psicólogos e pacientes...")
    conn.execute(text("DELETE FROM psicologos"))
    conn.execute(text("DELETE FROM pacientes"))

def popular_psicologos(conn, quantidade: int = 100) -> int:
    query = text("""
        INSERT INTO psicologos (primeiro_nome, ultimo_nome, crp, email, senha_hash)
        VALUES (:p_nome, :u_nome, :crp, :email, :s_hash)
    """)
    
    logger.info(f"Gerando {quantidade} psicólogos com e-mails vinculados e validados...")
    
    for _ in range(quantidade):
        p_nome = fake.first_name()
        u_nome = fake.last_name()
        
        # 1. Geramos um CRP aleatório de 7 dígitos
        crp = str(fake.random_number(digits=7, fix_len=True))
        
        # 2. Criamos o domínio aleatório
        dominio = fake.free_email_domain()
        
        # 3. Montamos o e-mail base e REMOVEMOS espaços (essencial para nomes compostos)
        # O .replace(" ", "") mata o erro que você viu no terminal!
        email_bruto = f"{p_nome.lower()}.{u_nome.lower()}@{dominio}".replace(" ", "")
        
        # 4. Normalização: Remove acentos (ex: 'André' vira 'andre')
        # Isso garante que o EmailStr do Pydantic aceite o dado
        email_limpo = (
            unicodedata.normalize('NFKD', email_bruto)
            .encode('ascii', 'ignore')
            .decode('ascii')
        )
        
        # 5. Criptografia usando seu módulo Security oficial
        senha_hash = Security.hash_password("SenhaTeste123")
        
        conn.execute(query, {
            "p_nome": p_nome,
            "u_nome": u_nome,
            "crp": crp,
            "email": email_limpo,
            "s_hash": senha_hash
        })
        
    return quantidade

def popular_pacientes(conn, quantidade: int = 20) -> int:
    query = text("""
        INSERT INTO pacientes (primeiro_nome, ultimo_nome, email, senha_hash)
        VALUES (:p_nome, :u_nome, :email, :s_hash)
    """)
    
    logger.info(f"Gerando {quantidade} pacientes...")
    for _ in range(quantidade):
        p_nome = fake.first_name()
        u_nome = fake.last_name()
        email = fake.unique.email()
        senha_hash = Security.hash_password("PacienteTeste123")
        
        conn.execute(query, {
            "p_nome": p_nome, 
            "u_nome": u_nome, 
            "email": email, 
            "s_hash": senha_hash
        })
    return quantidade

def popular_banco():
    engine = connect_db()
    if engine is None:
        raise RuntimeError("Falha na conexão.")

    with engine.begin() as conn:
        limpar_banco(conn)
        total_ps = popular_psicologos(conn, 100)
        #total_pac = popular_pacientes(conn, 30) 

    return total_ps

if __name__ == "__main__":
    try:
        ps_count = popular_banco()
        print("\n" + "="*30)
        print("BANCO POPULADO")
        print(f"Psicólogos criados: {ps_count}")
        print(f"Senha padrão: SenhaTeste123")
        print("="*30)
    except Exception as exc:
        logger.error(f"Erro: {exc}")
    