from google_auth_oauthlib.flow import Flow 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
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

    def listar_eventos(self, refresh_token: str, inicio: datetime, fim: datetime):
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
        
        # Formatando as datas para o padrão exigido pelo Google (RFC3339)
        time_min = inicio.isoformat() + 'Z' if inicio.tzinfo is None else inicio.isoformat()
        time_max = fim.isoformat() + 'Z' if fim.tzinfo is None else fim.isoformat()
        
        logger.info(f"Buscando eventos na agenda primária de {time_min} a {time_max}")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])


if __name__ == "__main__":
    from managers.psicologo import PsicologoManager
    from data.database import connect_db
    from datetime import datetime, timedelta, time, timezone

    print("--- INICIANDO TESTE ISOLADO DE LEITURA DA AGENDA ---")

    try:
        # 1. Instancia o manager e pega o token do banco direto na fonte
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

            # 3. Definindo as datas: Hoje das 10h às 12h (Fuso de Brasília / GMT-3)
            # É importantíssimo colar o timezone nas datas pra API do Google não achar que é horário de Londres!
            fuso_br = timezone(timedelta(hours=-3))
            hoje = datetime.now(fuso_br).date()
            
            inicio_teste = datetime.combine(hoje, time(10, 0), tzinfo=fuso_br)
            fim_teste = datetime.combine(hoje, time(12, 0), tzinfo=fuso_br)

            # 4. Busca os eventos usando apenas a função nova
            eventos = service.listar_eventos(refresh_token, inicio_teste, fim_teste)

            print(f"\n🎉 SUCESSO! Foram encontrados {len(eventos)} eventos hoje entre 10h e 12h:")
            for evento in eventos:
                inicio_ev = evento['start'].get('dateTime', evento['start'].get('date'))
                titulo = evento.get('summary', 'Sem Título')
                print(f" -> {inicio_ev} | {titulo}")

    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        print(f"Teste falhou com erro: {e}")

    

