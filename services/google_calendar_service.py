from google_auth_oauthlib.flow import Flow 
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


if __name__ == "__main__":
    TEST_CLIENT_SECRETS = "credentials.json"
    TEST_SCOPES = ["https://www.googleapis.com/auth/calendar"]
    TEST_REDIRECT_URI = "http://127.0.0.1:8000/api/agendamentos/google-callback"

    print("--- Iniciando Teste do Fluxo Web ---")

    try:
        # 2. Instancia o serviço
        service = GoogleCalendarService(
            client_secrets_file=TEST_CLIENT_SECRETS,
            scopes=TEST_SCOPES,
            redirect_uri=TEST_REDIRECT_URI
        )

        # 3. Gera a URL
        url = service.get_auth_url()
        print(f"\n1) Acesse essa URL no seu navegador:\n{url}")
        
        # 4. Pede para o usuário colar o código recebido no redirecionamento
        print("\n2) Após aprovar, você será levado para uma página de 'Erro' no 127.0.0.1 (já que seu servidor backend não está rodando agora).")
        print("Tranquilo! Apenas olhe para barra de endereço do navegador. Vai ter algo como:")
        print("http://127.0.0.1:8000/.../?state=...&code=4/0Aci9...&scope=...")
        
        codigo_copiado = input("\n3) Copie apenas a parte do código (depois de 'code=' e antes de '&scope=') e cole aqui: ")

        # 5. Troca o código pela credencial
        credenciais = service.exchange_code_for_token(codigo_copiado)

        print(f"\n--- SUCESSO! ---")
        print(f"Access Token: {credenciais.token}")
        print(f"Refresh Token: {credenciais.refresh_token}")
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        print(f"Teste falhou com erro: {e}")

    

