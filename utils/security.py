import bcrypt

class Security:
    
    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        # Encodifica para bytes, faz o hash, e decodifica o resultado para string
        senha_bytes = password.encode('utf-8')
        hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt(rounds=rounds))
        
        return hash_bytes.decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        # Pega a string do usuário e a do banco, transforma ambas em bytes e compara
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

if __name__ == '__main__':
    senha = 'GOAT of Genros'
    meu_hash = Security.hash_password(senha)
    print(meu_hash)
    print(Security.check_password(senha, meu_hash)) 