from fastapi import APIRouter, HTTPException, status, Depends, Request
from services.google_calendar_service import GoogleCalendarService
from managers.psicologo import PsicologoManager
from data.database import connect_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_psico_manager():
    engine = connect_db()
    return PsicologoManager(engine=engine, tabela="psicologos")

gc_service_singleton = GoogleCalendarService(
    client_secrets_file="credentials.json", 
    scopes=["https://www.googleapis.com/auth/calendar"], 
    redirect_uri="http://127.0.0.1:8000/api/agendamentos/google-callback"
)

def get_gc_service():
    return gc_service_singleton

@router.get("/google-login")
def google_login(service: GoogleCalendarService = Depends(get_gc_service)):
    """
    Endpoint 1: Gera a URL de permissão do Google e devolve para o Frontend.
    """
    try:
        logger.info("Gerando URL de autorização do Google Calendar")
        url = service.get_auth_url()
        return {"url": url}
    except Exception as e:
        logger.error(f"Erro ao gerar URL de auth: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar URL do Google")


@router.get("/google-callback")
def google_callback(
    code: str, 
    service: GoogleCalendarService = Depends(get_gc_service),
    manager: PsicologoManager = Depends(get_psico_manager)
):
    """
    Endpoint 2: Recebe o código do Google, troca pelo Refresh Token e salva no banco de dados.
    """
    try:
        logger.info("Recebido código do Google via callback, trocando por token...")
        credenciais = service.exchange_code_for_token(code)
        
        refresh_token = credenciais.refresh_token
        
        if not refresh_token:
            logger.warning("Atenção: Google não devolveu refresh_token (talvez o app não esteja forçando prompt='consent').")
            # Em modo de teste, às vezes o Google não manda se já houver permissão recente.
        
        # TODO IMPORTANTE: Atualizar psicologo_id fixo por DADOS DA SESSÃO REAL DO PSICÓLOGO LOGADO!

        # Futuramente, pegar do front o ID do psicólogo, para saber qual deles deverá ter sua coluna de google refresh token atualizada.
        psicologo_id = 1
        
        if refresh_token:
            sucesso = manager.atualizar_google_token(psicologo_id=psicologo_id, refresh_token=refresh_token)
            if not sucesso:
                raise HTTPException(status_code=500, detail="Falha ao salvar o token na tabela de psicólogos.")
            logger.info("Refresh Token salvo no banco com sucesso!")
                
        # Esse JSON (ou um Redirect para o Frontend) é o que o usuário vai ver como tela final
        return {"mensagem": "Calendário sincronizado com sucesso!", "psicologo_id": psicologo_id}
        
    except Exception as e:
        logger.error(f"Erro no callback do Google: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a autenticação do Google")
