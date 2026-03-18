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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS Customizado para o Dashboard High-Fidelity
st.markdown("""
    <style>
    /* Estilização Geral e Fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar - Fundo cinza ligeiramente mais claro */
    section[data-testid="stSidebar"] {
        background-color: #1e1e1e !important;
        border-right: 1px solid #333333;
    }
    
    /* Highlight Azul na Sidebar (O st.radio) */
    div.row-widget.stRadio > div {
        background: transparent;
    }
    div.row-widget.stRadio > div > label {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        transition: all 0.3s ease;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:focus-within {
        background-color: #007bff20; /* Subtle background change */
        border-left: 4px solid #007bff; /* Blue highlight bar */
    }

    /* Título Prominente */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Container (Cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e1e1e !important;
        border: 1px solid #333;
        border-radius: 8px !important;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Inputs (Text Fields) */
    div[data-baseweb="input"] {
        background-color: #2b2b2b !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] > input {
        color: #fff !important;
    }

    /* Botões Padrões e Primary */
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

    /* Tabela de Dados (DataGrid) Alternating rows natively supported by dark mode theme, 
       just ensuring text is white and clean */
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

# ================================
# Telas (Views)
# ================================

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
            
            # Using st.dataframe for a clean, sleek datagrid
            st.dataframe(
                df,
                column_config={
                    "id": st.column_config.NumberColumn("ID"),
                    "crp": st.column_config.TextColumn("CRP"),
                    "primeiro_nome": "Primeiro Nome",
                    "ultimo_nome": "Último Nome",
                    "email": "E-mail"
                },
                hide_index=True,
                use_container_width=True
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
                    st.success(f"✅ Psicólogo cadastrado com sucesso. ID gerado: {novo_id}")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])

def render_busca(manager: PsicologoManager) -> None:
    st.markdown("### Buscar por CRP")

    with st.container(border=True):
        crp = st.text_input("Digite o CRP para buscar", key="busca_crp")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Buscar", key="buscar_psicologo", type="primary", use_container_width=True):
            if not crp.strip():
                st.warning("⚠️ Informe um CRP válido.")
                return

            psicologo = manager.buscar_por_crp(crp.strip())
            if psicologo is None:
                st.error("Nenhum psicólogo encontrado para esse CRP.")
                return

            st.success("✅ Registro Encontrado!")
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
                st.warning("⚠️ Informe o CRP do psicólogo.")
                return

            try:
                payload = PsicologoUpdate(
                    primeiro_nome=limpar_campo(primeiro_nome),
                    ultimo_nome=limpar_campo(ultimo_nome),
                    email=limpar_campo(email),
                    senha=limpar_campo(senha),
                )
                manager.update_psicologo(crp.strip(), payload)
                st.success("✅ Atualização enviada. Confira a listagem para validar o resultado.")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])

def render_exclusao(manager: PsicologoManager) -> None:
    st.markdown("### Remover psicólogo")

    with st.container(border=True):
        st.markdown("<p style='color:#ccc;'>Informe o CRP do registro que deseja <b>apagar permanentemente</b>.</p>", unsafe_allow_html=True)
        crp = st.text_input("CRP do psicólogo que será removido", key="delete_crp")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Remover Cadastro", type="primary", use_container_width=True):
            if not crp.strip():
                st.warning("⚠️ Informe um CRP.")
                return

            removido = manager.delete_psicologo(crp.strip())
            if removido:
                st.success(f"✅ Psicólogo (CRP: {crp.strip()}) removido com sucesso.")
            else:
                st.error("Nenhum psicólogo encontrado com esse CRP.")

# ================================
# Main App
# ================================
def main() -> None:
    
    st.sidebar.markdown("<h2 style='text-align: center; color: white;'>Painel de Psicólogos</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    menu = [
        "📋 Listar Psicólogos", 
        "🔍 Buscar Psicólogo", 
        "➕ Cadastrar Psicólogo", 
        "✏️ Atualizar Psicólogo", 
        "🗑️ Remover Psicólogo"
    ]
    
    escolha = st.sidebar.radio("Navegação", menu, label_visibility="collapsed")

    # Main area Prominent Title
    st.markdown("<h1>Interface do banco de dados</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        manager = get_psicologo_manager()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    if escolha == "📋 Listar Psicólogos":
        render_listagem(manager)
    elif escolha == "🔍 Buscar Psicólogo":
        render_busca(manager)
    elif escolha == "➕ Cadastrar Psicólogo":
        render_cadastro(manager)
    elif escolha == "✏️ Atualizar Psicólogo":
        render_atualizacao(manager)
    elif escolha == "🗑️ Remover Psicólogo":
        render_exclusao(manager)

if __name__ == "__main__":
    main()