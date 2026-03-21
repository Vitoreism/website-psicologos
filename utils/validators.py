import re

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