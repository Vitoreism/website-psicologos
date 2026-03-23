import re
from email_validator import validate_email, EmailNotValidError

def validar_senha(senha: str) -> tuple[bool, str]:
    """
    Valida a senha e retorna uma tupla: (Sucesso, Mensagem de Erro ou Vazia)
    """
    if not (8 <= len(senha) <= 32):
        return False, "A senha deve ter entre 8 e 32 caracteres."
        
    if not re.search(r"[A-Z]", senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
        
    if not re.search(r"[a-z]", senha):
        return False, "A senha deve conter pelo menos uma letra minúscula."
        
    if not re.search(r"\d", senha):
        return False, "A senha deve conter pelo menos um número."
        
    if re.search(r"\s", senha):
        return False, "A senha não pode conter espaços em branco."
        
    return True, "" 

def validar_regras_email(email: str) -> tuple[bool, str]:
    """
    Valida a sintaxe do e-mail, verifica a existência do domínio (MX Records) 
    e bloqueia provedores temporários.
    """
    try:
        email_info = validate_email(email, check_deliverability=True)
        dominio = email_info.domain
        
        dominios_bloqueados = [
            "tempmail.com", "yopmail.com", "mailinator.com", "guerrillamail.com"
        ]
        
        if dominio in dominios_bloqueados:
            return False, "Provedores de e-mail temporário não são permitidos."

        return True, ""
        
    except EmailNotValidError:
        return False, "O e-mail fornecido possui um formato inválido ou o domínio não existe."


if __name__ == '__main__':
    # Bateria de testes para a validação de e-mail
    emails_para_teste = [
        # 1. Casos de Sucesso (Sintaxe correta e domínios reais)
        ("vitoreism@gmail.com", True),
        ("contato@outlook.com", True),
        ("clinica.machado@uol.com.br", True), 

        # 2. Casos de Falha na Sintaxe
        ("vitor@gmail", False),       # Faltando o TLD (.com)
        ("@hotmail.com", False),      # Faltando o usuário
        ("vitor.gmail.com", False),   # Faltando o @
        ("vitor @yahoo.com", False),  # Espaço em branco no e-mail

        # 3. Casos de Falha de DNS (Domínios que não existem)
        ("usuario@gmaillll.con", False), # Erro de digitação comum
        ("teste@meudominioinventado12345.com.br", False), 

        # 4. Casos de Bloqueio (Blacklist de E-mails Temporários)
        ("hacker@mailinator.com", False),
        ("spam@yopmail.com", False),
    ]

    print("--- Iniciando testes de validação de E-mail ---")
    todos_passaram = True
    
    for email, resultado_esperado in emails_para_teste:
        sucesso, mensagem = validar_regras_email(email)
        
        if sucesso == resultado_esperado:
            print(f"✅ [PASSOU] {email}")
        else:
            todos_passaram = False
            print(f"❌ [FALHOU] {email} | Esperado: {resultado_esperado}, Retornou: {sucesso}")
            print(f"   Motivo retornado: {mensagem}")

    if todos_passaram:
        print("\n🚀 Todos os testes passaram! A função está pronta para a API.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique a lógica.")