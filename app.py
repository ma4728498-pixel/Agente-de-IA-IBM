import os
import re
import sys
import json
import pathlib
import streamlit as st
from dotenv import load_dotenv

# Carrega credenciais: prioridade st.secrets (Streamlit Cloud) > .env (local)
load_dotenv()

def _get_secret(key: str) -> str:
    """Lê credencial do st.secrets (Streamlit Cloud) ou do ambiente (local/.env)."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

ORCHESTRATE_URL     = _get_secret("ORCHESTRATE_URL")
ORCHESTRATE_API_KEY = _get_secret("ORCHESTRATE_API_KEY")

def _setup_orchestrate_config():
    """
    Gera config.yaml + credentials.yaml do SDK WXO em tempo de execução.
    Obtém um token JWT IBM IAM a partir da API key e o armazena no formato
    exato que o SDK espera — substituindo o 'orchestrate env activate'.
    """
    if not ORCHESTRATE_URL or not ORCHESTRATE_API_KEY:
        return

    import time
    import yaml as _yaml

    # Gera token IAM a partir da API key
    token, expiry = "", int(time.time()) + 3600
    try:
        from ibm_cloud_sdk_core import IAMTokenManager
        tm = IAMTokenManager(apikey=ORCHESTRATE_API_KEY)
        resp = tm.request_token()
        token  = resp.get("access_token", "")
        expiry = resp.get("expiration", expiry)
    except Exception:
        pass

    config_dir = pathlib.Path.home() / ".config" / "orchestrate"
    cache_dir  = pathlib.Path.home() / ".cache"  / "orchestrate"
    config_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # config.yaml — inclui 'local' (PROTECTED_ENV_NAME exigido pelo SDK) + 'cloud' ativo
    config_data = {
        "cached_user_env": {},
        "context": {"active_environment": "cloud", "active_workspace": "Global workspace"},
        "environments": {
            "local": {"wxo_url": "http://localhost:4321"},
            "cloud": {"auth_type": "ibm_iam", "wxo_url": ORCHESTRATE_URL},
        },
        "python_registry": {"skip_version_check": False, "test_package_version_override": None, "type": "pypi"},
    }
    with open(config_dir / "config.yaml", "w", encoding="utf-8") as f:
        _yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, width=100000)

    # credentials.yaml — token JWT; width=100000 evita quebra de linha no token longo
    creds_data = {
        "auth": {
            "cloud": {"wxo_mcsp_token": token, "wxo_mcsp_token_expiry": expiry},
            "local": None,
        }
    }
    with open(cache_dir / "credentials.yaml", "w", encoding="utf-8") as f:
        _yaml.dump(creds_data, f, allow_unicode=True, default_flow_style=False, width=100000)

_setup_orchestrate_config()

# Garante codificação UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configuração da Página
st.set_page_config(
    page_title="Agente de Conformidade de Compras VF",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada — IBM Carbon Design System
st.markdown("""
<style>
    /* ── Tipografia e base ── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
    }

    /* ── Cabeçalho principal ── */
    .main-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: #161616;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 0.875rem;
        color: #6f6f6f;
        margin-bottom: 0;
        font-weight: 400;
    }
    .ibm-accent {
        color: #0f62fe;
        font-weight: 700;
    }

    /* ── Badge de status ── */
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 2px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #defbe6;
        color: #0e6027;
        margin-bottom: 0.75rem;
        letter-spacing: 0.01em;
    }

    /* ── Cards de conformidade ── */
    .conformidade-card {
        background: #f4f4f4;
        border-left: 3px solid #0f62fe;
        padding: 0.875rem 1.125rem;
        margin-bottom: 0.75rem;
        border-radius: 0 4px 4px 0;
    }
    .conformidade-card.aprovacao {
        border-left-color: #da1e28;
        background: #fff1f1;
    }
    .conformidade-card.ok {
        border-left-color: #24a148;
        background: #defbe6;
    }

    /* ── Cards de contato ── */
    .contato-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: 2px solid #0f62fe;
        border-radius: 0 0 4px 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* ── Seção de upload ── */
    .upload-section {
        background: #f4f4f4;
        border: 1px dashed #a8a8a8;
        border-radius: 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .upload-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #525252;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #f4f4f4;
        border-right: 1px solid #e0e0e0;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #525252;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
    }

    /* ── Botões ── */
    .stButton > button {
        border-radius: 0 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        border: 1px solid #8d8d8d !important;
        background: #ffffff !important;
        color: #161616 !important;
        transition: background 0.1s, border-color 0.1s !important;
    }
    .stButton > button:hover {
        background: #e8e8e8 !important;
        border-color: #525252 !important;
    }

    /* ── Chat ── */
    .stChatMessage {
        border-radius: 0 !important;
        border-bottom: 1px solid #e0e0e0;
    }
    .stChatInputContainer {
        border-top: 2px solid #0f62fe !important;
    }

    /* ── Divisor lateral ── */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 0.75rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# RENDERIZAÇÃO ENRIQUECIDA DA RESPOSTA
# ==========================================

def _md(texto: str) -> str:
    """Remove marcadores markdown ** e * mantendo o texto limpo."""
    return re.sub(r'\*+', '', texto).strip()


def _html_bloco(bloco: str) -> str:
    """Converte um bloco de conformidade (formato markdown do agente) em HTML visual."""

    # STATUS — aceita com ou sem ** ao redor
    status_match = re.search(r'\*{0,2}STATUS DE CONFORMIDADE:\*{0,2}\s*\*{0,2}(.+?)\*{0,2}\s*$', bloco, re.MULTILINE)
    if not status_match:
        return ""
    status = _md(status_match.group(1))
    requer = "Requer" in status
    card_class = "aprovacao" if requer else "ok"
    status_emoji = "🔴" if requer else "🟢"

    empresa_match = re.search(r'\*{0,2}EMPRESA:\*{0,2}\s*\*{0,2}(.+?)\*{0,2}\s*$', bloco, re.MULTILINE)
    pedido_match  = re.search(r'\*{0,2}PEDIDO/REFERÊNCIA:\*{0,2}\s*\*{0,2}(.+?)\*{0,2}\s*$', bloco, re.MULTILINE)
    empresa = _md(empresa_match.group(1)) if empresa_match else ""
    pedido  = _md(pedido_match.group(1))  if pedido_match  else ""

    html = (
        f'<div class="conformidade-card {card_class}">'
        f'<strong>{status_emoji} {status}</strong><br>'
        f'<span style="font-size:1.05rem"><strong>{empresa}</strong></span>'
        f'{"&nbsp;&nbsp;—&nbsp;&nbsp;" + pedido if pedido else ""}'
        f'</div>'
    )

    # CRITÉRIOS — linhas com SIM ou NÃO
    criterios_match = re.search(
        r'\*{0,2}CRITÉRIOS VERIFICADOS:\*{0,2}(.*?)(?=\*{0,2}CONTATOS ACIONADOS|\*{0,2}MODELOS DE E-MAIL|────|$)',
        bloco, re.DOTALL
    )
    if criterios_match:
        linhas = [
            _md(l.strip().lstrip("•-").strip())
            for l in criterios_match.group(1).splitlines()
            if re.search(r'\bSIM\b|\bNÃO\b', l, re.IGNORECASE)
        ]
        if linhas:
            items = ""
            for linha in linhas:
                icone = "❌" if re.search(r'\bSIM\b', linha, re.IGNORECASE) else "✅"
                items += f'<li style="margin-bottom:4px">{icone} {linha}</li>'
            html += (
                f'<p style="margin:0.8rem 0 0.3rem"><strong>Critérios verificados:</strong></p>'
                f'<ul style="margin:0;padding-left:1.2rem;line-height:1.8">{items}</ul>'
            )

    # CONTATOS — formato markdown: "- **Contato 1:** Nome (**Cargo**)"
    contatos_match = re.search(
        r'\*{0,2}CONTATOS ACIONADOS PARA APROVAÇÃO:\*{0,2}(.*?)(?=────|\*{0,2}MODELOS DE E-MAIL|$)',
        bloco, re.DOTALL
    )
    if contatos_match:
        bloco_contatos = contatos_match.group(1)
        # Captura: nome, cargo, email (com hífen especial ‑ ou normal -), tel, status
        contatos = re.findall(
            r'Contato \d+[:\*\s]+([^\n\(]+)\(([^\)]+)\)[^\n]*\n'
            r'[^\n]*E[\-‑]mail:\s*(\S+)\s*\|\s*Tel:\s*([^\n]+)\n'
            r'[^\n]*Status:\s*([^\n]+)',
            bloco_contatos
        )
        if contatos:
            cards = ""
            for nome, cargo, email, tel, status_c in contatos:
                email_clean = re.sub(r'\*+', '', email).strip()
                cards += (
                    f'<div class="contato-card">'
                    f'👤 <strong>{_md(nome)}</strong>'
                    f'<span style="color:#6f6f6f;font-size:0.85rem"> ({_md(cargo)})</span><br>'
                    f'📧 <a href="mailto:{email_clean}">{email_clean}</a><br>'
                    f'📞 {_md(tel)}<br>'
                    f'<span style="color:#6f6f6f;font-size:0.85rem">⏳ {_md(status_c)}</span>'
                    f'</div>'
                )
            html += (
                f'<p style="margin:0.8rem 0 0.3rem"><strong>Contatos acionados:</strong></p>'
                f'<div style="display:flex;gap:0.8rem;flex-wrap:wrap">{cards}</div>'
            )

    # E-MAILS — tudo após "MODELOS DE E-MAIL" em um <details>
    emails_match = re.search(
        r'(?:────+[^\n]*\n)?\*{0,2}MODELOS DE E[\-‑]MAIL[^\n]*\*{0,2}\n(?:────+[^\n]*\n)?(.*)',
        bloco, re.DOTALL
    )
    if emails_match:
        conteudo_email = emails_match.group(1).strip()
        # Remove linhas que são apenas referências à ferramenta (não conteúdo real)
        eh_referencia = bool(re.search(r'Veja o conteúdo|resposta da ferramenta|enviar_solicitacao', conteudo_email))
        if conteudo_email and not eh_referencia:
            safe = (conteudo_email
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))
            html += (
                f'<details style="margin-top:0.8rem">'
                f'<summary style="cursor:pointer;font-weight:600">📧 Ver modelos de e-mail para envio</summary>'
                f'<pre style="margin-top:0.5rem;background:#f4f4f4;padding:0.8rem;border-radius:4px;'
                f'font-size:0.82rem;white-space:pre-wrap;line-height:1.5">{safe}</pre>'
                f'</details>'
            )
        elif requer:
            html += (
                f'<p style="margin-top:0.8rem;color:#6f6f6f;font-size:0.9rem">'
                f'📧 E-mails de aprovação gerados e enviados aos contatos acima.</p>'
            )

    return html


def render_resposta(texto: str):
    """Renderiza a resposta completa do agente."""
    if not texto:
        return

    if "STATUS DE CONFORMIDADE:" not in texto:
        st.markdown(texto)
        return

    # Texto introdutório antes do primeiro bloco
    partes = re.split(r'(?=\*{0,2}STATUS DE CONFORMIDADE:)', texto, maxsplit=1)
    if len(partes) > 1 and partes[0].strip():
        st.markdown(partes[0].strip())

    blocos = [b.strip() for b in re.split(r'(?=\*{0,2}STATUS DE CONFORMIDADE:)', texto) if b.strip()]
    blocos_html = [_html_bloco(b) for b in blocos]
    html_total = "<hr style='margin:1rem 0'>".join(h for h in blocos_html if h)
    if html_total:
        st.markdown(html_total, unsafe_allow_html=True)


# ==========================================
# FUNÇÕES DE INTERAÇÃO COM WATSONX ORCHESTRATE
# ==========================================

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


# ==========================================
# INICIALIZAÇÃO DO ESTADO
# ==========================================

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
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem">
        <svg width="28" height="11" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="4" height="16" fill="#0f62fe"/><rect x="6" y="4" width="4" height="8" fill="#0f62fe"/>
            <rect x="12" y="0" width="4" height="16" fill="#0f62fe"/><rect x="18" y="4" width="4" height="8" fill="#0f62fe"/>
            <rect x="24" y="0" width="4" height="16" fill="#0f62fe"/><rect x="30" y="4" width="4" height="8" fill="#0f62fe"/>
            <rect x="36" y="0" width="4" height="16" fill="#0f62fe"/>
        </svg>
        <span style="font-weight:700;font-size:1.1rem">Painel de Controle</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="badge-status">● Agente Conectado (IBM WXO)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem;color:#6f6f6f;margin-bottom:0.5rem">
        Powered by <strong>IBM watsonx Orchestrate</strong><br>
        RAG: <strong>watsonx KB</strong><br>
        Desenvolvido com <strong>IBM Bob</strong>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown("### 📄 Ingestão de Documento")

    atalho_selecionado = None

    arquivo_pdf = st.file_uploader(
        "Enviar nota fiscal (PDF)",
        type=["pdf"],
        help="PDF de nota fiscal com texto selecionável (não escaneado)"
    )

    if arquivo_pdf is not None:
        if st.button("📄 Processar Nota Fiscal PDF", use_container_width=True, key="btn_pdf"):
            try:
                import pdfplumber, io
                with pdfplumber.open(io.BytesIO(arquivo_pdf.read())) as pdf:
                    texto_pdf = "\n".join(p.extract_text() or "" for p in pdf.pages)
                prompt_pdf = (
                    f"Ana Paula recebeu esta nota fiscal em PDF para verificação de conformidade. "
                    f"Extraia os dados (empresa, fornecedores, valor total, localização, período) "
                    f"e verifique se requer aprovação:\n\n"
                    f"{texto_pdf}"
                )
            except Exception as e:
                prompt_pdf = f"Erro ao ler o PDF: {e}"
            if "atalho_pdf" not in st.session_state:
                st.session_state["atalho_pdf"] = prompt_pdf
            st.rerun()

    if "atalho_pdf" in st.session_state:
        atalho_selecionado = st.session_state.pop("atalho_pdf")

    arquivo_invoice = st.file_uploader(
        "Enviar invoice (JSON)",
        type=["json"],
        help="Formato: invoice com campos invoice_id, empresa, line_items e valor_total"
    )

    if arquivo_invoice is not None:
        conteudo_invoice = arquivo_invoice.read().decode("utf-8")
        if st.button("🔍 Processar Invoice JSON", use_container_width=True, key="btn_invoice"):
            prompt_invoice = (
                f"Ana Paula recebeu uma invoice para verificação de conformidade. "
                f"Analise cada item desta invoice e verifique se requer aprovação:\n\n"
                f"{conteudo_invoice}"
            )
            if "atalho_invoice" not in st.session_state:
                st.session_state["atalho_invoice"] = prompt_invoice
            st.rerun()

    if "atalho_invoice" in st.session_state:
        atalho_selecionado = st.session_state.pop("atalho_invoice")

    arquivo_csv = st.file_uploader(
        "Enviar lote de transações (CSV)",
        type=["csv"],
        help="Colunas: empresa_id, pedido_id, valor_total, fornecedores (separados por |), localizacao"
    )

    if arquivo_csv is not None:
        conteudo_csv = arquivo_csv.read().decode("utf-8")
        if st.button("📊 Analisar Lote CSV", use_container_width=True, key="btn_csv"):
            prompt_csv = (
                f"Ana Paula enviou o arquivo de transações de compras. "
                f"Analise todas as empresas abaixo e identifique divergências:\n\n"
                f"{conteudo_csv}"
            )
            if "atalho_csv" not in st.session_state:
                st.session_state["atalho_csv"] = prompt_csv
            st.rerun()

    if "atalho_csv" in st.session_state:
        atalho_selecionado = st.session_state.pop("atalho_csv")

    st.markdown("---")
    st.markdown("### ⚡ Ações Rápidas")

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

# Cabeçalho principal — IBM Carbon style
st.markdown("""
<div style="display:flex;align-items:flex-start;justify-content:space-between;padding:1.25rem 0 1rem 0;border-bottom:2px solid #0f62fe;margin-bottom:1.25rem">
    <div>
        <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:#6f6f6f;margin-bottom:0.4rem">
            IBM watsonx Orchestrate · Agent Mode
        </div>
        <div class="main-header">Agente de Conformidade de Compras</div>
        <div class="sub-header" style="margin-top:0.3rem">
            Verificação automática de conformidade · Ingestão de documentos · Aprovação integrada
        </div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;padding-top:4px">
        <div style="display:flex;align-items:center;gap:8px">
            <svg width="32" height="13" viewBox="0 0 40 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="4" height="16" fill="#0f62fe"/>
                <rect x="6" y="4" width="4" height="8" fill="#0f62fe"/>
                <rect x="12" y="0" width="4" height="16" fill="#0f62fe"/>
                <rect x="18" y="4" width="4" height="8" fill="#0f62fe"/>
                <rect x="24" y="0" width="4" height="16" fill="#0f62fe"/>
                <rect x="30" y="4" width="4" height="8" fill="#0f62fe"/>
                <rect x="36" y="0" width="4" height="16" fill="#0f62fe"/>
            </svg>
            <span style="font-weight:700;color:#0f62fe;font-size:1rem;letter-spacing:-0.01em">IBM</span>
        </div>
        <span style="font-size:0.7rem;color:#8d8d8d;font-weight:400">Desenvolvido com IBM Bob</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Exibe o histórico de mensagens
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_resposta(msg["content"])
        else:
            st.markdown(msg["content"])
        if "reasoning" in msg and msg["reasoning"]:
            with st.expander("🧠 Ver Trilha de Raciocínio"):
                st.json(msg["reasoning"])

# Processamento de entrada
prompt_usuario = st.chat_input("Digite uma instrução para o agente (ex: Verificar Outubro/2026 da EMP-007)...")
if atalho_selecionado:
    prompt_usuario = atalho_selecionado

if prompt_usuario:
    st.session_state["messages"].append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Consultando a base de conhecimento e verificando conformidade..."):
            resposta, reasoning, erro = enviar_mensagem(prompt_usuario, include_reasoning=show_reasoning)

            if erro:
                texto_resposta = f"⚠️ Ocorreu um erro ao comunicar com o agente: `{erro}`"
                st.error(texto_resposta)
                st.session_state["messages"].append({"role": "assistant", "content": texto_resposta})
            else:
                render_resposta(resposta)
                if show_reasoning and reasoning:
                    with st.expander("🧠 Ver Trilha de Raciocínio"):
                        st.json(reasoning)

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": resposta,
                    "reasoning": reasoning if show_reasoning else None
                })

# Rodapé
st.markdown("""
<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #e0e0e0;
            text-align:center;font-size:0.78rem;color:#6f6f6f">
    Desenvolvido com
    <strong style="color:#0f62fe">IBM Bob</strong> ·
    <strong>IBM watsonx Orchestrate</strong> ·
    <strong>IBM Granite</strong> ·
    <strong>Streamlit</strong>
    <br>IBM SkillsBuild AI Experiential Learning Lab for Brazil
</div>
""", unsafe_allow_html=True)
