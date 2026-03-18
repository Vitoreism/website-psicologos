import streamlit as st
from pydantic import ValidationError

from data.database import connect_db
from managers.psicologo import PsicologoManager
from schemas.psicologo_schemas import PsicologoCreate, PsicologoUpdate


TABLE_NAME = "psicologos"


@st.cache_resource
def get_psicologo_manager() -> PsicologoManager:
    engine = connect_db()
    if engine is None:
        raise RuntimeError("Nao foi possivel conectar ao banco de dados. Verifique o arquivo .env.")
    return PsicologoManager(engine=engine, tabela=TABLE_NAME)


def carregar_psicologos(manager: PsicologoManager) -> list[dict]:
    psicologos = manager.read_psicologos()
    return [psicologo.model_dump() for psicologo in psicologos]


def limpar_campo(valor: str) -> str | None:
    valor_limpo = valor.strip()
    return valor_limpo or None


def render_listagem(manager: PsicologoManager) -> None:
    st.subheader("Psicologos cadastrados")
    psicologos = carregar_psicologos(manager)

    if not psicologos:
        st.info("Nenhum psicologo cadastrado.")
        return

    st.dataframe(psicologos, use_container_width=True, hide_index=True)


def render_cadastro(manager: PsicologoManager) -> None:
    st.subheader("Cadastrar psicologo")

    with st.form("form_cadastro_psicologo", clear_on_submit=True):
        primeiro_nome = st.text_input("Primeiro nome")
        ultimo_nome = st.text_input("Ultimo nome")
        crp = st.text_input("CRP")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Cadastrar")

    if not submit:
        return

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
            st.error("Nao foi possivel cadastrar o psicologo.")
            return
        st.success(f"Psicologo cadastrado com sucesso. ID gerado: {novo_id}")
    except ValidationError as exc:
        st.error(exc.errors()[0]["msg"])


def render_busca(manager: PsicologoManager) -> None:
    st.subheader("Buscar por CRP")

    crp = st.text_input("Digite o CRP para buscar", key="busca_crp")
    if st.button("Buscar", key="buscar_psicologo"):
        if not crp.strip():
            st.warning("Informe um CRP.")
            return

        psicologo = manager.buscar_por_crp(crp.strip())
        if psicologo is None:
            st.warning("Nenhum psicologo encontrado para esse CRP.")
            return

        st.json(psicologo.model_dump())


def render_atualizacao(manager: PsicologoManager) -> None:
    st.subheader("Atualizar psicologo")

    with st.form("form_atualizar_psicologo"):
        crp = st.text_input("CRP do psicologo que sera atualizado")
        primeiro_nome = st.text_input("Novo primeiro nome")
        ultimo_nome = st.text_input("Novo ultimo nome")
        email = st.text_input("Novo email")
        senha = st.text_input("Nova senha", type="password")
        submit = st.form_submit_button("Atualizar")

    if not submit:
        return

    if not crp.strip():
        st.warning("Informe o CRP do psicologo.")
        return

    try:
        payload = PsicologoUpdate(
            primeiro_nome=limpar_campo(primeiro_nome),
            ultimo_nome=limpar_campo(ultimo_nome),
            email=limpar_campo(email),
            senha=limpar_campo(senha),
        )
        manager.update_psicologo(crp.strip(), payload)
        st.success("Atualizacao enviada. Confira a listagem para validar o resultado.")
    except ValidationError as exc:
        st.error(exc.errors()[0]["msg"])


def render_exclusao(manager: PsicologoManager) -> None:
    st.subheader("Remover psicologo")

    crp = st.text_input("CRP do psicologo que sera removido", key="delete_crp")
    if st.button("Remover", type="primary"):
        if not crp.strip():
            st.warning("Informe um CRP.")
            return

        removido = manager.delete_psicologo(crp.strip())
        if removido:
            st.success("Psicologo removido com sucesso.")
        else:
            st.warning("Nao foi encontrado psicologo com esse CRP.")


def main() -> None:
    st.set_page_config(page_title="Painel de Psicologos", layout="wide")
    st.title("Interface do banco de dados")
    st.caption("CRUD inicial em Streamlit para a tabela de psicologos.")

    try:
        manager = get_psicologo_manager()
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        render_listagem(manager)
        st.divider()
        render_busca(manager)

    with col2:
        render_cadastro(manager)
        st.divider()
        render_atualizacao(manager)
        st.divider()
        render_exclusao(manager)


if __name__ == "__main__":
    main()
