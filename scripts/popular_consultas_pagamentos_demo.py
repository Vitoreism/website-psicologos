import argparse
import calendar
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from random import Random
from zoneinfo import ZoneInfo

from sqlalchemy import text


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.database import connect_db


TZ = ZoneInfo("America/Sao_Paulo")
DEMO_EMAIL_DOMAIN = "eloterapeutico.local"
DEMO_EMAIL_PREFIX = "demo.financeiro"
PAYMENT_METHODS = (
    "pix",
    "cartao_credito",
    "cartao_debito",
    "transferencia",
    "dinheiro",
    "plano_de_saude",
)
TIME_SLOTS = (
    (8, 0),
    (9, 30),
    (11, 0),
    (13, 30),
    (15, 0),
    (16, 30),
    (18, 0),
)
CONSULTATION_VALUES = (
    Decimal("90.00"),
    Decimal("110.00"),
    Decimal("130.00"),
    Decimal("150.00"),
    Decimal("180.00"),
    Decimal("220.00"),
    Decimal("260.00"),
)
MONTH_TARGETS = (8, 10, 12, 14, 16, 18)
FIRST_NAMES = (
    "Ana",
    "Bruno",
    "Camila",
    "Daniel",
    "Eduarda",
    "Felipe",
    "Gabriela",
    "Helena",
    "Igor",
    "Julia",
    "Lucas",
    "Marina",
    "Nicolas",
    "Paula",
    "Rafael",
    "Vitor",
)
LAST_NAMES = (
    "Almeida",
    "Barbosa",
    "Cardoso",
    "Dantas",
    "Esteves",
    "Farias",
    "Gomes",
    "Henriques",
    "Lima",
    "Melo",
    "Nogueira",
    "Pereira",
    "Queiroz",
    "Ribeiro",
    "Silva",
    "Mosqueiro",
)


@dataclass(frozen=True)
class PsicologoAlvo:
    id: int
    primeiro_nome: str
    ultimo_nome: str
    email: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Popula pacientes, consultas e pagamentos demo para apresentacao."
    )
    parser.add_argument(
        "--psicologo-id",
        type=int,
        help="ID do psicologo que recebera os dados demo. Se omitido, usa o ultimo cadastrado.",
    )
    parser.add_argument(
        "--psicologo-email",
        help="Email do psicologo alvo. Ignorado se --psicologo-id for informado.",
    )
    parser.add_argument(
        "--quantidade-pacientes",
        type=int,
        default=12,
        help="Quantidade de pacientes demo ativos para manter. Padrao: 12.",
    )
    parser.add_argument(
        "--meses",
        type=int,
        default=6,
        help="Quantidade de meses para distribuir as consultas. Padrao: 6.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed para reproduzir a mesma massa de dados. Padrao: 42.",
    )
    return parser.parse_args()


def shift_month(reference: date, months_back: int) -> tuple[int, int]:
    zero_based_month = reference.month - 1 - months_back
    year = reference.year + zero_based_month // 12
    month = zero_based_month % 12 + 1
    return year, month


def get_target_months(reference: date, total_months: int) -> list[tuple[int, int]]:
    return [shift_month(reference, months_back) for months_back in reversed(range(total_months))]


def get_month_targets(total_months: int) -> list[int]:
    if total_months <= len(MONTH_TARGETS):
        return list(MONTH_TARGETS[-total_months:])

    targets = list(MONTH_TARGETS)
    while len(targets) < total_months:
        targets.insert(0, max(6, targets[0] - 2))
    return targets


def resolve_psicologo(conn, psicologo_id: int | None, psicologo_email: str | None) -> PsicologoAlvo:
    if psicologo_id is not None:
        row = conn.execute(
            text(
                """
                SELECT id, primeiro_nome, ultimo_nome, email
                FROM psicologos
                WHERE id = :id
                """
            ),
            {"id": psicologo_id},
        ).mappings().first()
    elif psicologo_email:
        row = conn.execute(
            text(
                """
                SELECT id, primeiro_nome, ultimo_nome, email
                FROM psicologos
                WHERE email = :email
                """
            ),
            {"email": psicologo_email},
        ).mappings().first()
    else:
        row = conn.execute(
            text(
                """
                SELECT id, primeiro_nome, ultimo_nome, email
                FROM psicologos
                ORDER BY id DESC
                LIMIT 1
                """
            )
        ).mappings().first()

    if row is None:
        raise RuntimeError(
            "Nao foi possivel encontrar o psicologo alvo. Informe --psicologo-id ou --psicologo-email."
        )

    return PsicologoAlvo(
        id=row["id"],
        primeiro_nome=row["primeiro_nome"],
        ultimo_nome=row["ultimo_nome"],
        email=row["email"],
    )


def cleanup_demo_data(conn, psicologo_id: int) -> None:
    email_pattern = f"{DEMO_EMAIL_PREFIX}.{psicologo_id}.%@{DEMO_EMAIL_DOMAIN}"

    conn.execute(
        text(
            """
            DELETE FROM consultas
            WHERE id_psicologo = :id_psicologo
              AND id_paciente IN (
                  SELECT id_paciente
                  FROM pacientes
                  WHERE id_psicologo = :id_psicologo
                    AND email LIKE :email_pattern
              )
            """
        ),
        {"id_psicologo": psicologo_id, "email_pattern": email_pattern},
    )

    conn.execute(
        text(
            """
            DELETE FROM pagamentos
            WHERE id_psicologo = :id_psicologo
              AND id_paciente IN (
                  SELECT id_paciente
                  FROM pacientes
                  WHERE id_psicologo = :id_psicologo
                    AND email LIKE :email_pattern
              )
            """
        ),
        {"id_psicologo": psicologo_id, "email_pattern": email_pattern},
    )

    conn.execute(
        text(
            """
            DELETE FROM pacientes
            WHERE id_psicologo = :id_psicologo
              AND email LIKE :email_pattern
            """
        ),
        {"id_psicologo": psicologo_id, "email_pattern": email_pattern},
    )


def upsert_demo_patients(conn, psicologo_id: int, quantity: int, rng: Random) -> list[dict]:
    query = text(
        """
        INSERT INTO pacientes (id_psicologo, primeiro_nome, ultimo_nome, email, is_ativo)
        VALUES (:id_psicologo, :primeiro_nome, :ultimo_nome, :email, TRUE)
        ON CONFLICT (id_psicologo, email)
        DO UPDATE
        SET primeiro_nome = EXCLUDED.primeiro_nome,
            ultimo_nome = EXCLUDED.ultimo_nome,
            is_ativo = TRUE
        RETURNING id_paciente, primeiro_nome, ultimo_nome, email
        """
    )

    patients = []
    for index in range(quantity):
        first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(index + rng.randint(0, len(LAST_NAMES) - 1)) % len(LAST_NAMES)]
        email = f"{DEMO_EMAIL_PREFIX}.{psicologo_id}.{index + 1}@{DEMO_EMAIL_DOMAIN}"
        row = conn.execute(
            query,
            {
                "id_psicologo": psicologo_id,
                "primeiro_nome": first_name,
                "ultimo_nome": last_name,
                "email": email,
            },
        ).mappings().one()
        patients.append(dict(row))

    return patients


def build_consultation_plan(
    patients: list[dict],
    total_months: int,
    seed: int,
    reference_date: date,
) -> list[dict]:
    rng = Random(seed)
    plans = []
    month_targets = get_month_targets(total_months)
    target_months = get_target_months(reference_date, total_months)

    for month_index, ((year, month), total_consultations) in enumerate(zip(target_months, month_targets)):
        _, last_day = calendar.monthrange(year, month)

        for entry_index in range(total_consultations):
            patient = patients[(entry_index + month_index) % len(patients)]
            hour, minute = TIME_SLOTS[(entry_index * 2 + month_index) % len(TIME_SLOTS)]
            duration_minutes = 50 + (entry_index % 3) * 10
            base_day = 2 + (entry_index * 2 % 26)
            day = min(base_day, last_day)
            consultation_date = date(year, month, day)
            start_at = datetime(year, month, day, hour, minute, tzinfo=TZ)
            end_at = start_at + timedelta(minutes=duration_minutes)
            payment_method = PAYMENT_METHODS[(entry_index + month_index) % len(PAYMENT_METHODS)]
            base_value = CONSULTATION_VALUES[(entry_index + month_index * 2) % len(CONSULTATION_VALUES)]
            variation = Decimal(rng.choice((0, 5, 10, 15)))
            value = base_value + variation
            payment_timestamp = start_at - timedelta(hours=1)

            plans.append(
                {
                    "id_paciente": patient["id_paciente"],
                    "dia": consultation_date,
                    "horario_inicio": start_at,
                    "horario_fim": end_at,
                    "valor": value,
                    "metodo_pagamento": payment_method,
                    "data_pagamento": payment_timestamp,
                    "mes_referencia": consultation_date.strftime("%Y-%m"),
                }
            )

    return plans


def insert_consultations_and_payments(conn, psicologo_id: int, plans: list[dict]) -> dict:
    insert_payment = text(
        """
        INSERT INTO pagamentos (id_psicologo, id_paciente, valor, metodo_pagamento, data_pagamento)
        VALUES (:id_psicologo, :id_paciente, :valor, :metodo_pagamento, :data_pagamento)
        RETURNING id_pagamento
        """
    )
    insert_consulta = text(
        """
        INSERT INTO consultas (id_psicologo, id_paciente, id_pagamento, dia, horario_inicio, horario_fim)
        VALUES (:id_psicologo, :id_paciente, :id_pagamento, :dia, :horario_inicio, :horario_fim)
        RETURNING id_consulta
        """
    )

    per_method = Counter()
    per_month = Counter()
    total_value = Decimal("0.00")

    for plan in plans:
        payment_row = conn.execute(
            insert_payment,
            {
                "id_psicologo": psicologo_id,
                "id_paciente": plan["id_paciente"],
                "valor": plan["valor"],
                "metodo_pagamento": plan["metodo_pagamento"],
                "data_pagamento": plan["data_pagamento"],
            },
        ).mappings().one()

        conn.execute(
            insert_consulta,
            {
                "id_psicologo": psicologo_id,
                "id_paciente": plan["id_paciente"],
                "id_pagamento": payment_row["id_pagamento"],
                "dia": plan["dia"],
                "horario_inicio": plan["horario_inicio"],
                "horario_fim": plan["horario_fim"],
            },
        )

        per_method[plan["metodo_pagamento"]] += 1
        per_month[plan["mes_referencia"]] += 1
        total_value += plan["valor"]

    return {
        "consultas": len(plans),
        "pagamentos": len(plans),
        "valor_total": total_value,
        "por_metodo": per_method,
        "por_mes": per_month,
    }


def format_currency(value: Decimal) -> str:
    normalized = f"{value:.2f}"
    integer_part, decimal_part = normalized.split(".")
    groups = []
    while integer_part:
        groups.append(integer_part[-3:])
        integer_part = integer_part[:-3]
    return f"R$ {'.'.join(reversed(groups))},{decimal_part}"


def main() -> None:
    args = parse_args()
    engine = connect_db()
    if engine is None:
        raise RuntimeError("Falha ao conectar com o banco. Verifique o .env e o Postgres.")

    rng = Random(args.seed)
    reference_date = datetime.now(TZ).date()

    with engine.begin() as conn:
        psicologo = resolve_psicologo(conn, args.psicologo_id, args.psicologo_email)
        cleanup_demo_data(conn, psicologo.id)
        patients = upsert_demo_patients(conn, psicologo.id, args.quantidade_pacientes, rng)
        plans = build_consultation_plan(
            patients=patients,
            total_months=args.meses,
            seed=args.seed,
            reference_date=reference_date,
        )
        summary = insert_consultations_and_payments(conn, psicologo.id, plans)

    print("\n" + "=" * 56)
    print("MASSA DEMO DE CONSULTAS E PAGAMENTOS GERADA")
    print("=" * 56)
    print(
        f"Psicologo alvo : {psicologo.primeiro_nome} {psicologo.ultimo_nome} "
        f"(id={psicologo.id}, email={psicologo.email})"
    )
    print(f"Pacientes demo : {len(patients)}")
    print(f"Consultas      : {summary['consultas']}")
    print(f"Pagamentos     : {summary['pagamentos']}")
    print(f"Valor total    : {format_currency(summary['valor_total'])}")
    print("\nDistribuicao por metodo:")
    for method in PAYMENT_METHODS:
        print(f"  - {method}: {summary['por_metodo'].get(method, 0)}")
    print("\nDistribuicao por mes:")
    for month_key in sorted(summary["por_mes"]):
        print(f"  - {month_key}: {summary['por_mes'][month_key]}")
    print("\nReexecute quantas vezes quiser; o script substitui apenas os dados demo desse psicologo.")
    print(
        "Exemplo: venv\\Scripts\\python.exe scripts\\popular_consultas_pagamentos_demo.py "
        f"--psicologo-id {psicologo.id}"
    )


if __name__ == "__main__":
    main()
