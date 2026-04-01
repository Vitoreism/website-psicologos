from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from services.google_calendar_service import GoogleCalendarService
from managers.psicologo import PsicologoManager
from managers.consulta import ConsultaManager
from data.database import connect_db
import logging
from schemas.calendar_schemas import CreateEventRequest
from schemas.consulta_schemas import ConsultaCreate
from utils.auth import get_current_psicologo
from pydantic import Field
from decimal import Decimal
from datetime import date as date_type

logger = logging.getLogger(__name__)

router = APIRouter()

def get_psico_manager():
    engine = connect_db()
    return PsicologoManager(engine=engine, tabela="psicologos")

def get_consulta_manager():
    engine = connect_db()
    return ConsultaManager(engine=engine)


class AgendarConsultaRequest(CreateEventRequest):
    """
    Extensão do CreateEventRequest com dados necessários para
    persistir a consulta e o pagamento no banco de dados.
    """
    id_paciente: int = Field(description="ID do paciente vinculado ao psicólogo")
    dia: date_type = Field(description="Data da consulta (YYYY-MM-DD)")
    valor: Decimal = Field(gt=0, description="Valor cobrado pela consulta")
    metodo_pagamento: str = Field(
        min_length=2,
        max_length=30,
        description="Método: pix, cartao_credito, cartao_debito, dinheiro, transferencia"
    )

gc_service_singleton = GoogleCalendarService(
    client_secrets_file="credentials.json", 
    scopes=["https://www.googleapis.com/auth/calendar"], 
    redirect_uri="http://127.0.0.1:8000/api/agendamentos/google-callback"
)

def get_gc_service():
    return gc_service_singleton

@router.get("/google-login")
def google_login(
    service: GoogleCalendarService = Depends(get_gc_service),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Endpoint 1: Gera a URL de permissão do Google e devolve para o Frontend.
    """
    try:
        logger.info("Gerando URL de autorização do Google Calendar")
        url = service.get_auth_url(state=str(psicologo_id))
        return {"url": url}
    except Exception as e:
        logger.error(f"Erro ao gerar URL de auth: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar URL do Google")


@router.get("/google-callback")
def google_callback(
    code: str, 
    state: str = None,
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
        
        if not state:
            logger.error("State (psicologo_id) não recebido do Google.")
            raise HTTPException(status_code=400, detail="ID de sessão ausente no redirecionamento do Google.")
            
        psicologo_id = int(state)
        
        if refresh_token:
            sucesso = manager.atualizar_google_token(psicologo_id=psicologo_id, refresh_token=refresh_token)
            if not sucesso:
                raise HTTPException(status_code=500, detail="Falha ao salvar o token na tabela de psicólogos.")
            logger.info("Refresh Token salvo no banco com sucesso!")
                
        # Redireciona o navegador de volta para o dashboard do frontend
        return RedirectResponse(url="http://localhost:5173/dashboard?google=success")
        
    except HTTPException:
        return RedirectResponse(url="http://localhost:5173/dashboard?google=error")
    except Exception as e:
        logger.error(f"Erro no callback do Google: {e}")
        return RedirectResponse(url="http://localhost:5173/dashboard?google=error")


@router.post("/criar-agendamento", summary="Agendar consulta (Google Calendar + banco de dados)")
def criar_agendamento(
    request: AgendarConsultaRequest,
    service: GoogleCalendarService = Depends(get_gc_service),
    psico_manager: PsicologoManager = Depends(get_psico_manager),
    consulta_manager: ConsultaManager = Depends(get_consulta_manager),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Agenda uma consulta no Google Calendar e persiste a consulta + pagamento no banco.
    O pagamento é considerado realizado no ato do agendamento.
    """
    try:
        refresh_token = psico_manager.get_google_refresh_token(psicologo_id=psicologo_id)

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Psicólogo não possui agenda Google vinculada. Use /google-login primeiro."
            )

        # Verifica conflito de horário antes de criar
        eventos_existentes = service.listar_eventos(
            refresh_token=refresh_token,
            inicio=request.inicio,
            fim=request.fim,
            fuso_horario=request.fuso_horario
        )
        if eventos_existentes:
            logger.warning(f"Conflito de horário detectado para o psicólogo {psicologo_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um compromisso marcado neste horário."
            )

        # Cria o evento no Google Calendar
        evento_criado = service.criar_evento(
            refresh_token=refresh_token,
            titulo=request.titulo,
            inicio=request.inicio,
            fim=request.fim,
            descricao=request.descricao,
            fuso_horario=request.fuso_horario
        )

        # Persiste consulta + pagamento no banco de dados (transação atômica)
        consulta_data = ConsultaCreate(
            id_paciente=request.id_paciente,
            dia=request.dia,
            horario_inicio=request.inicio,
            horario_fim=request.fim,
            valor=request.valor,
            metodo_pagamento=request.metodo_pagamento,
        )

        consulta_salva = consulta_manager.criar_consulta_com_pagamento(
            consulta=consulta_data,
            id_psicologo=psicologo_id
        )

        if consulta_salva is None:
            logger.error(f"Evento criado no Google (id={evento_criado.get('id')}) mas falhou ao salvar no banco.")
            raise HTTPException(
                status_code=500,
                detail="Agendamento criado no Google Calendar, mas houve falha ao salvar no banco de dados."
            )

        logger.info(
            f"Consulta {consulta_salva.id_consulta} agendada com pagamento "
            f"{consulta_salva.id_pagamento} para psicólogo {psicologo_id}."
        )

        return {
            "mensagem": "Agendamento realizado com sucesso!",
            "id_consulta": consulta_salva.id_consulta,
            "id_pagamento": consulta_salva.id_pagamento,
            "id_google": evento_criado.get("id"),
            "link": evento_criado.get("htmlLink"),
        }

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.error(f"Erro inesperado ao criar agendamento: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar o agendamento."
        )


@router.get("/google-status")
def google_status(
    manager: PsicologoManager = Depends(get_psico_manager),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Verifica se o psicólogo já conectou o Google Calendar.
    """
    refresh_token = manager.get_google_refresh_token(psicologo_id=psicologo_id)
    return {"google_connected": refresh_token is not None and refresh_token != ""}


@router.post("/google-disconnect")
def google_disconnect(
    manager: PsicologoManager = Depends(get_psico_manager),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Remove a conexão do Google Calendar limpando o refresh_token do banco.
    """
    sucesso = manager.atualizar_google_token(psicologo_id=psicologo_id, refresh_token=None)
    if not sucesso:
        raise HTTPException(status_code=500, detail="Falha ao desconectar o Google Calendar.")
    logger.info(f"Google Calendar desconectado para psicologo_id={psicologo_id}")
    return {"mensagem": "Google Calendar desconectado com sucesso."}


@router.get("/listar-eventos")
def listar_eventos(
    inicio: str,
    fim: str,
    service: GoogleCalendarService = Depends(get_gc_service),
    manager: PsicologoManager = Depends(get_psico_manager),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Lista os eventos do Google Calendar do psicólogo para o período informado.
    Parâmetros inicio e fim devem ser ISO 8601, ex: 2026-03-01T00:00:00
    """
    from datetime import datetime

    try:
        refresh_token = manager.get_google_refresh_token(psicologo_id=psicologo_id)
        if not refresh_token:
            return {"eventos": []}

        inicio_dt = datetime.fromisoformat(inicio)
        fim_dt = datetime.fromisoformat(fim)

        eventos_google = service.listar_eventos(
            refresh_token=refresh_token,
            inicio=inicio_dt,
            fim=fim_dt,
            fuso_horario="America/Sao_Paulo"
        )

        # Formata para o frontend consumir facilmente
        eventos_formatados = []
        for ev in eventos_google:
            start = ev.get("start", {})
            end = ev.get("end", {})
            eventos_formatados.append({
                "id": ev.get("id"),
                "title": ev.get("summary", "Sem título"),
                "start": start.get("dateTime", start.get("date", "")),
                "end": end.get("dateTime", end.get("date", "")),
                "description": ev.get("description", ""),
            })

        return {"eventos": eventos_formatados}

    except Exception as e:
        logger.error(f"Erro ao listar eventos do Google Calendar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar eventos do Google Calendar.")


@router.delete("/deletar-evento/{event_id}")
def deletar_evento(
    event_id: str,
    service: GoogleCalendarService = Depends(get_gc_service),
    manager: PsicologoManager = Depends(get_psico_manager),
    psicologo_id: int = Depends(get_current_psicologo)
):
    """
    Remove um evento do Google Calendar pelo seu ID.
    """
    try:
        refresh_token = manager.get_google_refresh_token(psicologo_id=psicologo_id)
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Google Calendar não vinculado.")

        service.deletar_evento(refresh_token=refresh_token, event_id=event_id)
        logger.info(f"Evento {event_id} deletado para psicologo_id={psicologo_id}")
        return {"mensagem": "Evento removido com sucesso."}

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.error(f"Erro ao deletar evento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao remover o evento do Google Calendar.")