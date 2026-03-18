import streamlit as st
import pandas as pd
from pydantic import ValidationError

from data.database import connect_db
from managers.psicologo import PsicologoManager
from schemas.psicologo_schemas import PsicologoCreate, PsicologoUpdate

TABLE_NAME = "psicologos"

# 1. Configuração de Layout e Tema
st.set_page_config(
    page_title="Painel de Psicólogos",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS Customizado para o Dashboard
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #1e1e1e !important;
        border-right: 1px solid #333333;
    }

    section[data-testid="stSidebar"] .sidebar-card {
        background: transparent;
        border: 1px solid #343434;
        border-radius: 12px;
        padding: 18px 14px 10px 14px;
        margin-top: 10px;
    }
    section[data-testid="stSidebar"] .sidebar-card h2 {
        text-align: center;
        color: #ffffff;
        font-size: 1.3rem;
        margin: 0 0 16px 0;
        letter-spacing: -0.4px;
    }
    section[data-testid="stSidebar"] .nav-caption {
        color: #9c9c9c;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 10px;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.45rem;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px;
        padding: 0.6rem 0.75rem;
        margin: 0;
        transition: background-color 0.15s ease, border-color 0.15s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: #252525 !important;
        border-color: #333 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child {
        color: #f1f1f1 !important;
        font-weight: 500;
        font-size: 0.97rem;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: #252525 !important;
        border-color: #3a3a3a !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div:last-child {
        color: #ffffff !important;
    }

    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e1e1e !important;
        border: 1px solid #333;
        border-radius: 8px !important;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    div[data-baseweb="input"] {
        background-color: #2b2b2b !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] > input {
        color: #fff !important;
    }

    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s;
    }
    div.stButton > button[kind="primary"] {
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0056b3 !important;
    }

    thead tr th {
        background-color: #2b2b2b !important;
        color: #007bff !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_psicologo_manager() -> PsicologoManager:
    engine = connect_db()
    if engine is None:
        raise RuntimeError("Não foi possível conectar ao banco de dados. Verifique o arquivo .env.")
    return PsicologoManager(engine=engine, tabela=TABLE_NAME)

def carregar_psicologos(manager: PsicologoManager) -> list[dict]:
    psicologos = manager.read_psicologos()
    return [psicologo.model_dump() for psicologo in psicologos]

def limpar_campo(valor: str) -> str | None:
    valor_limpo = valor.strip()
    return valor_limpo or None

def formatar_nome_completo(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if not df.empty:
        df["nome_completo"] = df["primeiro_nome"] + " " + df["ultimo_nome"]
    return df

def render_sidebar() -> str:
    paginas = [
        "Relatório",
        "Listar Psicólogos",
        "Buscar Psicólogo",
        "Cadastrar Psicólogo",
        "Atualizar Psicólogo",
        "Remover Psicólogo",
    ]

    st.sidebar.markdown(
        """
        <div class="sidebar-card">
            <h2>Painel de Psicólogos</h2>
            <div class="nav-caption">Navegação</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return st.sidebar.radio(
        "Navegação",
        paginas,
        index=0,
        label_visibility="collapsed",
    )

# ================================
# Telas (Views)
# ================================

def render_relatorio(manager: PsicologoManager) -> None:
    st.markdown("### Relatório gerencial")

    with st.container(border=True):
        st.markdown(
            "<p style='color:#ccc;'>Resumo consolidado dos dados cadastrados no sistema.</p>",
            unsafe_allow_html=True,
        )

        relatorio = manager.gerar_relatorio()
        resumo = relatorio["resumo"]
        psicologos = formatar_nome_completo(pd.DataFrame(carregar_psicologos(manager)))
        total_pacientes = relatorio["total_pacientes"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Psicólogos cadastrados", resumo["total_psicologos"])
        c2.metric("CRPs únicos", resumo["total_crps_unicos"])
        c3.metric("E-mails únicos", resumo["total_emails_unicos"])
        c4.metric("Pacientes cadastrados", total_pacientes if total_pacientes is not None else "N/D")

        c5, c6 = st.columns(2)
        c5.metric("Primeiro ID cadastrado", resumo["primeiro_id_cadastrado"] or "N/D")
        c6.metric("Último ID cadastrado", resumo["ultimo_id_cadastrado"] or "N/D")

        st.divider()

        if psicologos.empty:
            st.info("Nenhum psicólogo cadastrado para compor o relatório.")
            return

        st.markdown("#### Distribuição por domínio de e-mail")
        dominios_df = pd.DataFrame(relatorio["dominios_email"])
        if dominios_df.empty:
            st.caption("Sem dados de domínio de e-mail para exibir.")
        else:
            st.dataframe(
                dominios_df,
                column_config={
                    "dominio_email": "Domínio",
                    "quantidade": st.column_config.NumberColumn("Quantidade"),
                },
                hide_index=True,
                use_container_width=True,
            )

        st.markdown("#### Base detalhada")
        base_relatorio = psicologos[["id", "nome_completo", "crp", "email"]]
        st.dataframe(
            base_relatorio,
            column_config={
                "id": st.column_config.NumberColumn("ID"),
                "nome_completo": "Nome completo",
                "crp": "CRP",
                "email": "E-mail",
            },
            hide_index=True,
            use_container_width=True,
        )

        csv_bytes = base_relatorio.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar relatório em CSV",
            data=csv_bytes,
            file_name="relatorio_psicologos.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )

def render_listagem(manager: PsicologoManager) -> None:
    st.markdown("### Psicólogos cadastrados")

    with st.container(border=True):
        st.markdown("<p style='color:#ccc; margin-bottom: 20px;'>Visualize todos os profissionais ativos no sistema.</p>", unsafe_allow_html=True)

        if st.button("Exibir / Mostrar todos os psicólogos", type="primary", use_container_width=True):
            psicologos = carregar_psicologos(manager)

            if not psicologos:
                st.info("Nenhum psicólogo cadastrado na base de dados.")
                return

            df = pd.DataFrame(psicologos)

            st.dataframe(
                df,
                column_config={
                    "id": st.column_config.NumberColumn("ID"),
                    "crp": st.column_config.TextColumn("CRP"),
                    "primeiro_nome": "Primeiro Nome",
                    "ultimo_nome": "Último Nome",
                    "email": "E-mail",
                },
                hide_index=True,
                use_container_width=True,
            )

def render_cadastro(manager: PsicologoManager) -> None:
    st.markdown("### Cadastrar psicólogo")

    with st.container(border=True):
        st.markdown("<p style='color:#ccc;'>Preencha os dados abaixo para criar um novo registro.</p>", unsafe_allow_html=True)

        with st.form("form_cadastro_psicologo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                primeiro_nome = st.text_input("Primeiro nome")
                ultimo_nome = st.text_input("Último nome")
                crp = st.text_input("CRP")
            with c2:
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)

        if submit:
            try:
                payload = PsicologoCreate(
                    primeiro_nome=primeiro_nome.strip(),
                    ultimo_nome=ultimo_nome.strip(),
                    crp=crp.strip(),
                    email=email.strip(),
                    senha=senha,
                )
                novo_id = manager.criar_psicologo(payload)
                if novo_id is None:
                    st.error("Erro: Não foi possível cadastrar o psicólogo. Verifique se o CRP já existe.")
                else:
                    st.success(f"Psicólogo cadastrado com sucesso. ID gerado: {novo_id}")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])

def render_busca(manager: PsicologoManager) -> None:
    st.markdown("### Buscar por CRP")

    with st.container(border=True):
        crp = st.text_input("Digite o CRP para buscar", key="busca_crp")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Buscar", key="buscar_psicologo", type="primary", use_container_width=True):
            if not crp.strip():
                st.warning("Informe um CRP válido.")
                return

            psicologo = manager.buscar_por_crp(crp.strip())
            if psicologo is None:
                st.error("Nenhum psicólogo encontrado para esse CRP.")
                return

            st.success("Registro encontrado.")
            st.json(psicologo.model_dump())

def render_atualizacao(manager: PsicologoManager) -> None:
    st.markdown("### Atualizar psicólogo")

    with st.container(border=True):
        with st.form("form_atualizar_psicologo"):
            st.markdown("<p style='color:#ccc;'>Informe o CRP do profissional e preencha os novos dados.</p>", unsafe_allow_html=True)

            crp = st.text_input("CRP do psicólogo que será atualizado")
            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                primeiro_nome = st.text_input("Novo primeiro nome")
                ultimo_nome = st.text_input("Novo último nome")
            with c2:
                email = st.text_input("Novo email")
                senha = st.text_input("Nova senha", type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Atualizar", type="primary", use_container_width=True)

        if submit:
            if not crp.strip():
                st.warning("Informe o CRP do psicólogo.")
                return

            try:
                payload = PsicologoUpdate(
                    primeiro_nome=limpar_campo(primeiro_nome),
                    ultimo_nome=limpar_campo(ultimo_nome),
                    email=limpar_campo(email),
                    senha=limpar_campo(senha),
                )
                manager.update_psicologo(crp.strip(), payload)
                st.success("Atualização enviada. Confira a listagem para validar o resultado.")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])

def render_exclusao(manager: PsicologoManager) -> None:
    st.markdown("### Remover psicólogo")

    with st.container(border=True):
        st.markdown("<p style='color:#ccc;'>Informe o CRP do registro que deseja <b>apagar permanentemente</b>.</p>", unsafe_allow_html=True)
        crp = st.text_input("CRP do psicólogo que será removido", key="delete_crp")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Remover cadastro", type="primary", use_container_width=True):
            if not crp.strip():
                st.warning("Informe um CRP.")
                return

            removido = manager.delete_psicologo(crp.strip())
            if removido:
                st.success(f"Psicólogo (CRP: {crp.strip()}) removido com sucesso.")
            else:
                st.error("Nenhum psicólogo encontrado com esse CRP.")

# ================================
# Main App
# ================================
def main() -> None:
    escolha = render_sidebar()

    st.markdown("<h1>Psicólogos hub</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        manager = get_psicologo_manager()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if escolha == "Relatório":
        render_relatorio(manager)
    elif escolha == "Listar Psicólogos":
        render_listagem(manager)
    elif escolha == "Buscar Psicólogo":
        render_busca(manager)
    elif escolha == "Cadastrar Psicólogo":
        render_cadastro(manager)
    elif escolha == "Atualizar Psicólogo":
        render_atualizacao(manager)
    elif escolha == "Remover Psicólogo":
        render_exclusao(manager)

if __name__ == "__main__":
    main()
