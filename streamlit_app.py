import streamlit as st
import pandas as pd
from pydantic import ValidationError

from data.database import connect_db
from managers.psicologo import PsicologoManager
from schemas.psicologo_schemas import PsicologoCreate, PsicologoUpdate


TABLE_NAME = "psicologos"

# -----------------
# Configuração Tema / Backend
# -----------------
st.set_page_config(
    page_title="Painel de Psicólogos", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the dashboard feel
st.markdown("""
<style>
    /* Metric Card Styling to stand out */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #2ECC71; /* Emerald Green for metrics */
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_psicologo_manager() -> PsicologoManager:
    try:
        engine = connect_db()
        if engine is None:
            raise RuntimeError("Não foi possível conectar ao banco de dados.")
        return PsicologoManager(engine=engine, tabela=TABLE_NAME)
    except Exception as e:
        raise RuntimeError(f"Falha de conexão: {e}")

def carregar_psicologos(manager: PsicologoManager) -> list[dict]:
    try:
        psicologos = manager.read_psicologos()
        return [psicologo.model_dump() for psicologo in psicologos]
    except Exception as e:
        st.error(f"Erro ao carregar psicólogos: {e}")
        return []

def limpar_campo(valor: str) -> str | None:
    valor_limpo = valor.strip()
    return valor_limpo or None

# -----------------
# Módulos de Visualização (Páginas)
# -----------------

def render_dashboard_home(manager: PsicologoManager):
    st.title("🏠 Dashboard Home")
    st.markdown("Bem-vindo ao **Painel de Controle**. Resumo atual da plataforma:")
    
    psicologos = carregar_psicologos(manager)
    total_psicologos = len(psicologos)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Psicólogos", f"{total_psicologos}")
    with col2:
        st.metric("Usuários Ativos (Simulado)", f"{int(total_psicologos * 0.9)}")
    with col3:
        st.metric("Status do Servidor", "Online ✨")
        
    st.divider()
    
    st.subheader("🔍 Busca Rápida por CRP")
    busca_rapida = st.text_input("Digite um CRP para acessar o perfil", placeholder="Ex: 12345/06", key="home_busca")
    if st.button("Buscar Rápido", type="primary"):
        if busca_rapida.strip():
            resultado = manager.buscar_por_crp(busca_rapida.strip())
            if resultado:
                st.success(f"✅ Encontrado: {resultado.primeiro_nome} {resultado.ultimo_nome} - E-mail: {resultado.email}")
            else:
                st.warning("CRP não localizado na base de dados.")
        else:
            st.info("Informe um CRP para buscar.")


def render_gestao_cadastros(manager: PsicologoManager):
    st.title("📋 Gestão de Cadastros")
    st.markdown("Gerencie a base de terapeutas. Adicione novos e visualize a tabela completa.")
    
    # Formulário de Cadastro (Expander)
    with st.expander("➕ Adicionar Novo Psicólogo", expanded=False):
        with st.form("form_cadastro_psicologo", clear_on_submit=False):
            col_a, col_b = st.columns(2)
            with col_a:
                primeiro_nome = st.text_input("Primeiro nome")
                ultimo_nome = st.text_input("Último nome")
                crp = st.text_input("CRP")
            with col_b:
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
            
            submit = st.form_submit_button("Cadastrar Psicólogo", type="primary", use_container_width=True)

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
                    st.error("Não foi possível cadastrar o psicólogo. O CRP ou E-mail podem já existir.")
                else:
                    st.success(f"✅ Psicólogo {primeiro_nome} cadastrado com sucesso! (Recarregue para ver na tabela)")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])
            except Exception as e:
                st.error(f"Erro inesperado: {e}")

    st.subheader("Bando de Dados (Visualização Avançada)")
    psicologos = carregar_psicologos(manager)
    
    if not psicologos:
        st.info("Nenhum psicólogo cadastrado no momento.")
    else:
        df = pd.DataFrame(psicologos)
        
        st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "crp": st.column_config.TextColumn("CRP", disabled=True),
                "primeiro_nome": "Nome",
                "ultimo_nome": "Sobrenome",
                "email": st.column_config.TextColumn("E-mail", format="mailto:%s")
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor_psicologos"
        )
        st.caption("A tabela fornece uma visualização interativa (ordenação e redimensionamento). As edições feitas no layout requerem a aba Busca e Edição para persistência no BD.")
        

def render_busca_edicao(manager: PsicologoManager):
    st.title("🔍 Busca, Edição e Remoção")
    st.markdown("Utilize o CRP para localizar, atualizar atributos ou excluir permanentemente um registro.")
    
    col_main, _, _ = st.columns([2,1,1])
    with col_main:
        crp_alvo = st.text_input("CRP do Psicólogo", help="O CRP é a chave única de identificação.", key="edicao_busca_crp")
    
    if not crp_alvo.strip():
        st.info("Digite um CRP para carregar as opções de edição e remoção.")
        return
        
    psicologo_data = manager.buscar_por_crp(crp_alvo.strip())
    
    if psicologo_data is None:
        st.error(f"⚠️ Nenhum psicólogo encontrado para o CRP: '{crp_alvo}'.")
        return
        
    st.divider()
    
    col_edit, col_del = st.columns([1.2, 1], gap="large")
    
    with col_edit:
        st.subheader("✏️ Atualizar Dados")
        with st.form("form_atualizar"):
            primeiro_nome = st.text_input("Nome", value=psicologo_data.primeiro_nome)
            ultimo_nome = st.text_input("Sobrenome", value=psicologo_data.ultimo_nome)
            email = st.text_input("E-mail", value=psicologo_data.email)
            senha = st.text_input("Nova Senha (deixe em branco para manter)", type="password")
            
            btn_update = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
            
        if btn_update:
            try:
                payload = PsicologoUpdate(
                    primeiro_nome=limpar_campo(primeiro_nome),
                    ultimo_nome=limpar_campo(ultimo_nome),
                    email=limpar_campo(email),
                    senha=limpar_campo(senha),
                )
                manager.update_psicologo(crp_alvo.strip(), payload)
                st.success("✅ Registro atualizado com sucesso no Banco de Dados!")
            except ValidationError as exc:
                st.error(exc.errors()[0]["msg"])
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
                
    with col_del:
        st.subheader("🗑️ Remover Conta")
        st.warning("⚠️ **Aviso:** Esta ação é irreversível e excluirá o cadastro completamente.")
        
        confirmar_delete = st.checkbox("Eu entendo os riscos e confirmo a exclusão", key="chk_del")
        if st.button("Deletar Psicólogo", type="primary", disabled=not confirmar_delete):
            try:
                removido = manager.delete_psicologo(crp_alvo.strip())
                if removido:
                    st.success(f"✅ Psicólogo(a) com CRP '{crp_alvo}' removido(a) com sucesso!")
                else:
                    st.error("Falha ao remover o registro ou registro já inexistente.")
            except Exception as e:
                st.error(f"Ocorreu um erro no banco: {e}")

# -----------------
# Main Exec
# -----------------
def main() -> None:
    try:
        manager = get_psicologo_manager()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as e:
        st.error(f"Erro grave: {e}")
        st.stop()

    # Sidebar setup
    st.sidebar.title("🧭 Navegação Principal")
    
    menu_opcoes = {
        "🏠 Dashboard Home": render_dashboard_home,
        "📋 Gestão de Cadastros": render_gestao_cadastros,
        "🔍 Busca e Edição": render_busca_edicao
    }
    
    escolha = st.sidebar.radio("Escolha a Tela:", list(menu_opcoes.keys()))
    
    st.sidebar.divider()
    st.sidebar.info("Sistema de gerenciamento de psicólogos - CRUD em Streamlit Profissional.", icon="ℹ️")

    # Render Active Page
    renderizar_pagina = menu_opcoes[escolha]
    renderizar_pagina(manager)

if __name__ == "__main__":
    main()
