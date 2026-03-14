import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.disable(logging.CRITICAL)  # silencia todos os logs do projeto

from sqlalchemy import text

from data.database import connect_db
from managers.psicologo import PsicologoManager


def main() -> None:
    engine = connect_db()
    if engine is None:
        print("Erro: não foi possível conectar ao banco.")
        sys.exit(1)

    print("\nO que você quer buscar?")
    print("  1 - Psicólogo por CRP")
    print("  2 - Paciente por email")
    opcao = input("Escolha (1 ou 2): ").strip()

    if opcao == "1":
        crp = input("Digite o CRP: ").strip()
        manager = PsicologoManager(engine=engine, tabela="psicologos")
        resultado = manager.buscar_por_crp(crp)

        if resultado:
            print("\n--- Psicólogo encontrado ---")
            print(f"  ID          : {resultado['id']}")
            print(f"  Nome        : {resultado['primeiro_nome']} {resultado['ultimo_nome']}")
            print(f"  CRP         : {resultado['crp']}")
            print(f"  Email       : {resultado['email']}")
        else:
            print(f"\nERRO : Nenhum psicólogo encontrado com CRP '{crp}'.")

    elif opcao == "2":
        email = input("Digite o email: ").strip()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT id, primeiro_nome, ultimo_nome, email FROM pacientes WHERE email = :email"),
                {"email": email},
            ).mappings().first()

        if row:
            print("\n--- Paciente encontrado ---")
            print(f"  ID           : {row['id']}")
            print(f"  Nome         : {row['primeiro_nome']} {row['ultimo_nome']}")
            print(f"  Email        : {row['email']}")
        else:
            print(f"\nERRO : Nenhum paciente encontrado com email '{email}'.")

    else:
        print("Opção indisponível. Use 1 ou 2.")


if __name__ == "__main__":
    main()
