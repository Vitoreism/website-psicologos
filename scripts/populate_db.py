import hashlib
import logging
import sys
from typing import Dict, List, Tuple
from pathlib import Path

from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.database import connect_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def hash_senha(senha: str) -> str:
    """Gera um hash simples para popular dados de exemplo."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


PSICOLOGOS: List[Dict[str, str]] = [
    {
        "primeiro_nome": "Vitor",
        "ultimo_nome": "Machado",
        "crp": "2424248",
        "email": "vitor@gmail.com",
        "senha": "Genrolindo123",
    },
    {
        "primeiro_nome": "Joana",
        "ultimo_nome": "Nogueira",
        "crp": "8787878",
        "email": "joana@exemplo.com",
        "senha": "SenhaForte456",
    },
    {
        "primeiro_nome": "Bruno",
        "ultimo_nome": "Santos",
        "crp": "5656565",
        "email": "bruno@exemplo.com",
        "senha": "OutraSenha789",
    },
]

PACIENTES: List[Dict[str, str]] = [
    {
        "primeiro_nome": "Ana",
        "ultimo_nome": "Silva",
        "email": "ana@exemplo.com",
        "senha": "Paciente123",
    },
    {
        "primeiro_nome": "Carlos",
        "ultimo_nome": "Souza",
        "email": "carlos@exemplo.com",
        "senha": "Paciente456",
    },
    {
        "primeiro_nome": "Marina",
        "ultimo_nome": "Lima",
        "email": "marina@exemplo.com",
        "senha": "Paciente789",
    },
]


def popular_psicologos(conn) -> int:
    query = text(
        """
        INSERT INTO psicologos (primeiro_nome, ultimo_nome, crp, email, senha_hash)
        VALUES (:primeiro_nome, :ultimo_nome, :crp, :email, :senha_hash)
        ON CONFLICT (crp) DO UPDATE
        SET
            primeiro_nome = EXCLUDED.primeiro_nome,
            ultimo_nome = EXCLUDED.ultimo_nome,
            email = EXCLUDED.email,
            senha_hash = EXCLUDED.senha_hash;
        """
    )

    total = 0
    for psicologo in PSICOLOGOS:
        conn.execute(
            query,
            {
                "primeiro_nome": psicologo["primeiro_nome"],
                "ultimo_nome": psicologo["ultimo_nome"],
                "crp": psicologo["crp"],
                "email": psicologo["email"],
                "senha_hash": hash_senha(psicologo["senha"]),
            },
        )
        total += 1

    return total


def popular_pacientes(conn) -> int:
    query = text(
        """
        INSERT INTO pacientes (primeiro_nome, ultimo_nome, email, senha_hash)
        SELECT :primeiro_nome, :ultimo_nome, :email, :senha_hash
        WHERE NOT EXISTS (
            SELECT 1 FROM pacientes
            WHERE email = :email
              AND primeiro_nome = :primeiro_nome
              AND ultimo_nome = :ultimo_nome
        );
        """
    )

    inseridos = 0
    for paciente in PACIENTES:
        result = conn.execute(
            query,
            {
                "primeiro_nome": paciente["primeiro_nome"],
                "ultimo_nome": paciente["ultimo_nome"],
                "email": paciente["email"],
                "senha_hash": hash_senha(paciente["senha"]),
            },
        )
        inseridos += result.rowcount

    return inseridos


def popular_banco() -> Tuple[int, int]:
    engine = connect_db()
    if engine is None:
        raise RuntimeError("Falha ao criar conexao com o banco.")

    with engine.begin() as conn:
        total_psicologos = popular_psicologos(conn)
        total_pacientes = popular_pacientes(conn)

    return total_psicologos, total_pacientes


if __name__ == "__main__":
    try:
        ps_count, pac_count = popular_banco()
        logger.info("Banco populado com sucesso.")
        logger.info("Psicologos processados: %s", ps_count)
        logger.info("Pacientes inseridos: %s", pac_count)
    except Exception as exc:
        logger.error("Erro ao popular banco: %s", exc)
        raise
