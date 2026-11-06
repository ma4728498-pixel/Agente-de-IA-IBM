import os
import sys
import json
import streamlit as st

# Garante codificação UTF-8 no Windows
sys.stdout.reconfigure(encoding="utf-8")

# Configuração da Página
st.set_page_config(
    page_title="Agente de Conformidade de Compras VF",
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

        agent_name = "agente_conformidade_VF"
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
                "👋 Olá! Sou o **Agente de Conformidade de Compras VF** no IBM watsonx Orchestrate.\n\n"
                "Verifico 3 critérios de conformidade em cada transação:\n"
                "- 💰 Valor total > 15% acima da média histórica\n"
                "- 🏭 Fornecedor não encontrado no histórico\n"
                "- 📍 Localização não encontrada no histórico\n\n"
                "Quando qualquer critério é detectado, envio automaticamente a solicitação "
                "de aprovação para os 2 contatos responsáveis da empresa."
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
                "content": "Conversa reiniciada. Como posso ajudá-lo na verificação de conformidade?"
            }
        ]
        st.session_state["thread_id"] = None
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ Ações Rápidas")

    atalho_selecionado = None
    if st.button("🔍 Verificar todas as empresas (Outubro/2026)", use_container_width=True):
        atalho_selecionado = (
            "Verifique a conformidade de todas as 8 empresas para o mês de Outubro/2026 "
            "e acione os aprovadores quando necessário."
        )

    if st.button("🏭 Checar fornecedores novos", use_container_width=True):
        atalho_selecionado = (
            "Liste apenas as empresas que possuem fornecedores novos em Outubro/2026, "
            "ou seja, fornecedores que não aparecem no histórico dos meses anteriores."
        )

    if st.button("📍 Checar localizações novas", use_container_width=True):
        atalho_selecionado = (
            "Liste apenas as empresas que possuem localização nova ou ausente em Outubro/2026."
        )

    if st.button("💰 Checar valores atípicos", use_container_width=True):
        atalho_selecionado = (
            "Liste apenas as empresas cujo valor total em Outubro/2026 é mais de 15% "
            "acima da média histórica."
        )

    st.markdown("---")
    st.markdown("### 📊 Dados da Knowledge Base")

    kb_path = "knowledge_base/docs/empresas_corporativas.json"
    if os.path.exists(kb_path):
        with st.expander("🏢 Empresas Corporativas (JSON)"):
            with open(kb_path, encoding="utf-8") as f:
                dados = json.load(f)
            empresas = dados if isinstance(dados, list) else dados.get("empresas", [])
            for emp in empresas:
                st.markdown(f"**{emp.get('nome', emp.get('empresa_nome', ''))}** — {emp.get('empresa_id', '')}")


# ==========================================
# ÁREA PRINCIPAL DE CHAT
# ==========================================
st.markdown('<div class="main-header">🛡️ Agente de Conformidade de Compras VF</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Verificação automática de conformidade integrada ao IBM watsonx Orchestrate</div>',
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
prompt_usuario = st.chat_input("Digite uma instrução para o agente (ex: Verificar Outubro/2026 da EMP-007)...")
if atalho_selecionado:
    prompt_usuario = atalho_selecionado

if prompt_usuario:
    # 1. Adiciona a mensagem do usuário ao histórico e exibe
    st.session_state["messages"].append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    # 2. Executa a chamada para o agente com indicador visual de progresso
    with st.chat_message("assistant"):
        with st.spinner("🤖 Consultando a base de conhecimento e verificando conformidade..."):
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
