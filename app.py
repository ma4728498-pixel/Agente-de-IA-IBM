import os
import sys
import pandas as pd
import streamlit as st

# Garante codificação UTF-8 no Windows
sys.stdout.reconfigure(encoding="utf-8")

# Configuração da Página
st.set_page_config(
    page_title="Analista de Conformidade de Compras",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #0f62fe;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #525252;
        margin-bottom: 1.5rem;
    }
    .badge-status {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #defbe6;
        color: #0e6027;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Funções de interação com o watsonx Orchestrate
@st.cache_resource
def get_orchestrate_clients():
    try:
        from ibm_watsonx_orchestrate.cli.commands.chat.chat_controller import (
            create_run_client,
            create_threads_client
        )
        from ibm_watsonx_orchestrate.cli.commands.agents.agents_helper import get_agent_id_by_name

        agent_name = "analista_conformidade_compras"
        agent_id = get_agent_id_by_name(agent_name)
        run_client = create_run_client()
        threads_client = create_threads_client()
        return run_client, threads_client, agent_id, agent_name, None
    except Exception as e:
        return None, None, None, None, str(e)


def enviar_mensagem(prompt: str, include_reasoning: bool = False):
    from ibm_watsonx_orchestrate.cli.commands.chat.chat_controller import execute_agent_interaction_with_fallback

    run_client, threads_client, agent_id, agent_name, error = get_orchestrate_clients()
    if error or not agent_id:
        return f"❌ Erro ao conectar ao agente: {error}", None, None

    thread_id = st.session_state.get("thread_id")

    try:
        resultado = execute_agent_interaction_with_fallback(
            run_client=run_client,
            threads_client=threads_client,
            message=prompt,
            agent_id=agent_id,
            include_reasoning=include_reasoning,
            agent_name=agent_name,
            thread_id=thread_id,
            return_agent_interaction_result=True
        )

        if resultado.status == "success":
            st.session_state["thread_id"] = resultado.thread_id
            return resultado.final_message, resultado.reasoning_trace, None
        else:
            return None, None, resultado.error or "Erro desconhecido na resposta do agente."
    except Exception as e:
        return None, None, str(e)


# Inicialização do Histórico de Conversa
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "👋 Olá! Sou o **Analista de Conformidade de Compras** no IBM watsonx Orchestrate.\n\n"
                "Estou pronto para auditar transações, verificar limites de tolerância (+15%), "
                "identificar registros sem localização e gerar notificações para a aprovação dupla."
            )
        }
    ]

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🛡️ Painel de Controle")
    st.markdown('<div class="badge-status">● Agente Conectado (IBM WXO)</div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Opções")
    show_reasoning = st.checkbox("Exibir trilha de raciocínio (Reasoning)", value=False)

    if st.button("🔄 Nova Conversa (Limpar Chat)", use_container_width=True):
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Conversa reiniciada. Como posso ajudá-lo na auditoria de compras?"
            }
        ]
        st.session_state["thread_id"] = None
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Ações Rápidas")
    
    atalho_selecionado = None
    if st.button("🔍 Auditar Todas as Compras", use_container_width=True):
        atalho_selecionado = (
            "Analise o histórico de compras, identifique quais transações possuem "
            "divergências ou dados faltantes e acione os aprovadores responsáveis."
        )

    if st.button("📍 Checar Localização Ausente", use_container_width=True):
        atalho_selecionado = (
            "Liste apenas as ordens de compra em que a localização de origem não foi informada."
        )

    if st.button("✅ Aprovar PED-006 (Ambos)", use_container_width=True):
        atalho_selecionado = (
            "Para o pedido PED-006, a Gerente de Compras Ana Paula Ferreira respondeu 'APROVADO' "
            "e o Diretor Financeiro Carlos Eduardo Lima respondeu 'APROVADO'. Atualize o status da operação."
        )

    if st.button("❌ Rejeitar PED-003", use_container_width=True):
        atalho_selecionado = (
            "Para o pedido PED-003, o Diretor Financeiro Carlos Eduardo Lima respondeu 'REJEITADO' "
            "devido ao preço excessivo. Atualize o status da operação."
        )

    st.markdown("---")
    st.markdown("### 📊 Dados da Knowledge Base")

    csv_path = "knowledge_base/docs/historico_compras.csv"
    if os.path.exists(csv_path):
        with st.expander("📁 Histórico de Compras (CSV)"):
            df_compras = pd.read_csv(csv_path)
            st.dataframe(df_compras, use_container_width=True, hide_index=True)

    aprovadores_path = "knowledge_base/docs/matriz_aprovadores.csv"
    if os.path.exists(aprovadores_path):
        with st.expander("👥 Matriz de Aprovadores (CSV)"):
            df_aprov = pd.read_csv(aprovadores_path)
            st.dataframe(df_aprov, use_container_width=True, hide_index=True)


# ==========================================
# ÁREA PRINCIPAL DE CHAT
# ==========================================
st.markdown('<div class="main-header">🛡️ Analista de Conformidade de Compras</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Interface de Gestão e Auditoria Automatizada integrada ao IBM watsonx Orchestrate</div>',
    unsafe_allow_html=True
)

# Exibe o histórico de mensagens
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "reasoning" in msg and msg["reasoning"]:
            with st.expander("🧠 Ver Trilha de Raciocínio"):
                st.json(msg["reasoning"])

# Processamento de entrada (seja pelo input de texto ou por um botão de atalho)
prompt_usuario = st.chat_input("Digite uma instrução para o agente (ex: Auditar compras recentes)...")
if atalho_selecionado:
    prompt_usuario = atalho_selecionado

if prompt_usuario:
    # 1. Adiciona a mensagem do usuário ao histórico e exibe
    st.session_state["messages"].append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    # 2. Executa a chamada para o agente com indicador visual de progresso
    with st.chat_message("assistant"):
        with st.spinner("🤖 Consultando a base de conhecimento e processando regras no watsonx Orchestrate..."):
            resposta, reasoning, erro = enviar_mensagem(prompt_usuario, include_reasoning=show_reasoning)

            if erro:
                texto_resposta = f"⚠️ Ocorreu um erro ao comunicar com o agente: `{erro}`"
                st.error(texto_resposta)
                st.session_state["messages"].append({"role": "assistant", "content": texto_resposta})
            else:
                st.markdown(resposta)
                if show_reasoning and reasoning:
                    with st.expander("🧠 Ver Trilha de Raciocínio"):
                        st.json(reasoning)

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": resposta,
                    "reasoning": reasoning if show_reasoning else None
                })
