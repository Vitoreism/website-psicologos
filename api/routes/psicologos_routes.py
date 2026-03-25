from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from schemas.psicologo_schemas import PsicologoCreate, PsicologoResponse, PsicologoLogin, PsicologoLoginResponse
from managers.psicologo import PsicologoManager
from data.database import connect_db
from typing import Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Função de Dependência para fornecer o Manager às rotas
def get_psico_manager():
    engine = connect_db()
    return PsicologoManager(engine=engine, tabela="psicologos")

@router.post("/", response_model=PsicologoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_psicologo(
    psico_in: PsicologoCreate, 
    manager: PsicologoManager = Depends(get_psico_manager)
):
    try:
        logger.info("Iniciando o cadastramento de psicologo")
        psico_criado_dict = manager.criar_psicologo(psico_in)
    except IntegrityError:
        logger.warning("Erro ao cadastrar psicologo: Já existe um psicólogo cadastrado com este e-mail ou CRP.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um psicólogo cadastrado com este e-mail ou CRP."
        )

    if not psico_criado_dict:
        logger.error("Erro ao cadastrar psicologo: Erro interno ao cadastrar psicólogo. Tente novamente mais tarde.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cadastrar psicólogo. Tente novamente mais tarde."
        )

    logger.info("Psicologo cadastrado com sucesso")
    # O FastAPI pega esse dicionário e valida contra o PsicologoResponse automaticamente
    return psico_criado_dict


@router.post("/login", response_model=PsicologoLoginResponse, status_code=status.HTTP_200_OK)
def login_psicologo(
    credenciais: PsicologoLogin,
    manager: PsicologoManager = Depends(get_psico_manager)
):
    logger.info("Iniciando login")
    logger.info
    psicologo_auth = manager.autenticar_psicologo(credenciais.email, credenciais.senha)
    
    if not psicologo_auth:
        logger.warning("Login invalido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
    logger.info("Login realizado com sucesso")
    return PsicologoLoginResponse(
        mensagem="Login realizado com sucesso",
        psicologo=psicologo_auth
    )