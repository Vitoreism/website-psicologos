from google_auth_oauthlib.flow import Flow 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
import pytz
import logging


logger = logging.getLogger(__name__)


class GoogleCalendarService:
    def __init__(self, client_secrets_file, scopes, redirect_uri):
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes
        self.redirect_uri = redirect_uri
        
        # Cria o Flow apenas uma vez para não perder o 'code_verifier' (PKCE) entre as chamadas do teste
        self.flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

    def get_auth_url(self):
        auth_url, _ = self.flow.authorization_url(prompt='consent', access_type='offline')
        logger.info(f'Generated auth URL: {auth_url}')
        return auth_url

    def exchange_code_for_token(self, code):
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        logger.info('Exchanged code for token successfully')
        return credentials

    def listar_eventos(self, refresh_token: str, inicio: datetime, fim: datetime, fuso_horario: str = "America/Sao_Paulo"):
        client_config = self.flow.client_config
        
        # O grande truque: Recriar a credencial usando apenas o refresh_token do banco!
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=client_config.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=client_config["client_id"],
            client_secret=client_config["client_secret"],
            scopes=self.scopes
        )
        
        # Constrói o client oficial do Google Calendar API v3
        service = build('calendar', 'v3', credentials=credentials)
        
        # Formatando as datas para UTC (RFC3339) — igual ao que o Google armazena os eventos
        # Se a datetime vier sem fuso (naive), interpreta como sendo do fuso_horario informado
        tz = pytz.timezone(fuso_horario)
        if inicio.tzinfo is None:
            inicio = tz.localize(inicio)
        if fim.tzinfo is None:
            fim = tz.localize(fim)

        time_min = inicio.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        time_max = fim.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        logger.info(f"Buscando eventos na agenda primária de {time_min} a {time_max}")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    def criar_evento(self, refresh_token: str, titulo: str, inicio: datetime, fim: datetime, descricao: str | None = None, fuso_horario: str = "America/Sao_Paulo") -> dict:
        client_config = self.flow.client_config

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=client_config.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=client_config["client_id"],
            client_secret=client_config["client_secret"],
            scopes=self.scopes
        )

        service = build('calendar', 'v3', credentials=credentials)

        # Montando o corpo do evento no formato que o Google exige
        evento_body = {
            "summary": titulo,
            "description": descricao,
            "start": {
                "dateTime": inicio.isoformat(),
                "timeZone": fuso_horario,
            },
            "end": {
                "dateTime": fim.isoformat(),
                "timeZone": fuso_horario,
            },
        }

        logger.info(f"Criando evento '{titulo}' de {inicio} a {fim}")

        evento_criado = service.events().insert(
            calendarId='primary',
            body=evento_body
        ).execute()

        logger.info(f"Evento criado com sucesso! ID: {evento_criado.get('id')}")
        return evento_criado


if __name__ == "__main__":
    from managers.psicologo import PsicologoManager
    from data.database import connect_db
    from datetime import datetime, timedelta, time, timezone

    print("--- INICIANDO TESTE DE CRIAÇÃO DE EVENTO ---")

    try:
        # 1. Pega o token do banco
        manager = PsicologoManager(engine=connect_db(), tabela="psicologos")
        refresh_token = manager.get_google_refresh_token(psicologo_id=1)

        if not refresh_token:
            print("❌ Erro: Psicólogo ID 1 não possui google_refresh_token salvo no banco.")
        else:
            print("✅ Token encontrado no banco! Conectando ao Google Calendar API...")

            # 2. Instancia o serviço
            service = GoogleCalendarService(
                client_secrets_file="credentials.json",
                scopes=["https://www.googleapis.com/auth/calendar"],
                redirect_uri="http://127.0.0.1:8000/api/agendamentos/google-callback"
            )

            # 3. Definindo datas do evento de teste: amanhã das 14h às 15h (Brasília)
            fuso_br = timezone(timedelta(hours=-3))
            amanha = (datetime.now(fuso_br) + timedelta(days=1)).date()

            inicio_evento = datetime.combine(amanha, time(14, 0), tzinfo=fuso_br)
            fim_evento    = datetime.combine(amanha, time(15, 0), tzinfo=fuso_br)

            # 4. Cria o evento chamando a função com parâmetros Python puros
            evento_criado = service.criar_evento(
                refresh_token=refresh_token,
                titulo="[TESTE] Consulta via Elo Terapêutico",
                inicio=inicio_evento,
                fim=fim_evento,
                descricao="Evento de teste criado automaticamente pelo backend.",
                fuso_horario="America/Sao_Paulo"
            )

            print(f"\n🎉 SUCESSO! Evento criado na agenda!")
            print(f" -> Título:  {evento_criado.get('summary')}")
            print(f" -> Início:  {evento_criado['start'].get('dateTime')}")
            print(f" -> Fim:     {evento_criado['end'].get('dateTime')}")
            print(f" -> Link:    {evento_criado.get('htmlLink')}")

    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        print(f"Teste falhou com erro: {e}")
