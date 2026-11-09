#!/usr/bin/env python3
"""
MCP Server — Agente de Conformidade VF
Expõe as ferramentas de conformidade de compras ao IBM Bob via protocolo MCP (stdio).

Ferramentas disponíveis:
  - listar_empresas              : lista todas as empresas com seus IDs e histórico resumido
  - obter_empresa                : retorna dados completos de uma empresa pelo ID ou nome
  - verificar_conformidade       : verifica se uma transação tem não-conformidades
  - enviar_solicitacao_aprovacao : gera e-mails formais de aprovação para os aprovadores
  - analisar_lote_csv            : ingere um arquivo CSV de transações e verifica todas de uma vez
"""

import csv
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve o caminho da knowledge base (relativo ao repo, não ao cwd)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
KB_PATH = ROOT / "knowledge_base" / "docs" / "empresas_corporativas.json"

from mcp.server.mcpserver import MCPServer

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
LIMIAR_INCOERENCIA = 15.0  # %


# ---------------------------------------------------------------------------
# Carrega a knowledge base em memória (uma vez ao iniciar)
# ---------------------------------------------------------------------------
def _carregar_kb() -> dict:
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


KB = _carregar_kb()

# ---------------------------------------------------------------------------
# Servidor MCP
# ---------------------------------------------------------------------------
server = MCPServer(
    name="conformidade-vf",
    description="Agente de Conformidade de Compras VF — verifica transações corporativas contra histórico e gera solicitações de aprovação.",
)


# ---------------------------------------------------------------------------
# Tool 1: listar_empresas
# ---------------------------------------------------------------------------
@server.tool()
def listar_empresas() -> str:
    """Lista todas as empresas cadastradas na base de conhecimento com seus IDs,
    nomes, cidades de operação e quantidade de meses no histórico.
    Use esta ferramenta primeiro para descobrir quais empresas estão disponíveis."""
    empresas = KB.get("empresas", [])
    resultado = []
    for emp in empresas:
        historico = emp.get("historico_mensal", [])
        localizacoes = list({m["localizacao"] for m in historico if "localizacao" in m})
        resultado.append({
            "id": emp["id"],
            "nome": emp["nome"],
            "meses_historico": len(historico),
            "localizacoes": localizacoes,
            "contatos": [c["nome"] for c in emp.get("contatos", [])],
        })
    return json.dumps(resultado, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 2: obter_empresa
# ---------------------------------------------------------------------------
@server.tool()
def obter_empresa(empresa_id: str = "", empresa_nome: str = "") -> str:
    """Retorna os dados completos de uma empresa: histórico mensal de compras,
    fornecedores por mês, localizações e contatos aprovadores.

    Forneça 'empresa_id' (ex: 'EMP-001') OU 'empresa_nome' (ex: 'Alpha Tech').
    A busca por nome é case-insensitive e por substring.
    """
    empresas = KB.get("empresas", [])
    encontrada = None

    if empresa_id:
        for emp in empresas:
            if emp["id"].strip().upper() == empresa_id.strip().upper():
                encontrada = emp
                break

    if not encontrada and empresa_nome:
        nome_lower = empresa_nome.strip().lower()
        for emp in empresas:
            if nome_lower in emp["nome"].lower():
                encontrada = emp
                break

    if not encontrada:
        return json.dumps({
            "erro": "Empresa não encontrada. Use listar_empresas() para ver as disponíveis.",
            "empresa_id_buscado": empresa_id,
            "empresa_nome_buscado": empresa_nome,
        }, ensure_ascii=False, indent=2)

    return json.dumps(encontrada, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 3: verificar_conformidade
# ---------------------------------------------------------------------------
@server.tool()
def verificar_conformidade(
    empresa_id: str,
    pedido_id: str,
    valor_total_atual: float,
    fornecedores_atuais: list[str],
    localizacao_atual: str,
) -> str:
    """Verifica se uma transação de compras tem não-conformidades comparando com
    o histórico da empresa na base de conhecimento.

    Critérios verificados automaticamente:
      1. Valor total > 15% acima da média histórica dos demais meses
      2. Fornecedor(es) não presentes no histórico de compras
      3. Localização não registrada no histórico

    Retorna 'requer_aprovacao: true' com a lista de divergências se qualquer
    critério for violado. Os dados históricos são buscados automaticamente
    a partir do empresa_id — não é necessário informá-los manualmente.
    O resultado inclui o campo 'contatos_aprovadores' pronto para uso em
    enviar_solicitacao_aprovacao().

    Args:
        empresa_id: ID da empresa (ex: 'EMP-001'). Use listar_empresas() para descobrir.
        pedido_id: Código ou referência do pedido / mês sendo analisado (ex: 'Novembro/2026').
        valor_total_atual: Valor total da transação em reais.
        fornecedores_atuais: Lista de nomes dos fornecedores da transação atual.
        localizacao_atual: Localização informada na transação (ex: 'São Paulo, SP').
    """
    # Busca empresa na KB
    empresa = None
    for emp in KB.get("empresas", []):
        if emp["id"].strip().upper() == empresa_id.strip().upper():
            empresa = emp
            break

    if not empresa:
        return json.dumps({
            "erro": f"Empresa '{empresa_id}' não encontrada. Use listar_empresas() para ver as disponíveis.",
        }, ensure_ascii=False, indent=2)

    historico = empresa.get("historico_mensal", [])
    empresa_nome = empresa["nome"]

    # Média histórica excluindo o mês do pedido (se já existir)
    valores_historicos = [
        m["valor_total"] for m in historico
        if m.get("mes", "").strip().lower() != pedido_id.strip().lower()
    ]
    media_historica = sum(valores_historicos) / len(valores_historicos) if valores_historicos else 0.0

    # Fornecedores e localizações históricas (excluindo o mês atual)
    fornecedores_historicos = list({
        f
        for m in historico
        for f in m.get("fornecedores", [])
        if m.get("mes", "").strip().lower() != pedido_id.strip().lower()
    })
    localizacoes_historicas = list({
        m["localizacao"]
        for m in historico
        if "localizacao" in m and m.get("mes", "").strip().lower() != pedido_id.strip().lower()
    })

    # --- Critério 1: Valor atípico ---
    divergencias = []
    variacao_percentual = 0.0
    valor_atipico = False
    if media_historica > 0:
        variacao_percentual = ((valor_total_atual - media_historica) / media_historica) * 100
        if variacao_percentual > LIMIAR_INCOERENCIA:
            valor_atipico = True
            divergencias.append(
                f"Valor total R${valor_total_atual:,.2f} está {variacao_percentual:.1f}% acima "
                f"da média histórica R${media_historica:,.2f} (limite: {LIMIAR_INCOERENCIA:.0f}%)"
            )

    # --- Critério 2: Fornecedores novos ---
    historicos_lower = {f.strip().lower() for f in fornecedores_historicos}
    fornecedores_novos: list[str] = []
    if historicos_lower:
        fornecedores_novos = [
            f for f in fornecedores_atuais
            if f.strip().lower() not in historicos_lower
        ]
    fornecedor_novo = len(fornecedores_novos) > 0
    if fornecedor_novo:
        divergencias.append(
            f"Fornecedor(es) não encontrado(s) no histórico: {', '.join(fornecedores_novos)}"
        )

    # --- Critério 3: Localização nova ---
    localizacao_ausente = not localizacao_atual or str(localizacao_atual).strip() == ""
    localizacao_nova = False
    if localizacao_ausente:
        divergencias.append("Localização da transação não informada")
        localizacao_nova = True
    else:
        historicos_loc_lower = {loc.strip().lower() for loc in localizacoes_historicas}
        if localizacao_atual.strip().lower() not in historicos_loc_lower:
            localizacao_nova = True
            divergencias.append(
                f"Localização '{localizacao_atual}' não registrada no histórico desta empresa"
            )

    requer_aprovacao = len(divergencias) > 0

    return json.dumps({
        "requer_aprovacao": requer_aprovacao,
        "empresa_nome": empresa_nome,
        "empresa_id": empresa_id,
        "pedido_id": pedido_id,
        "valor_total_atual": valor_total_atual,
        "media_historica_mensal": round(media_historica, 2),
        "variacao_percentual": round(variacao_percentual, 2),
        "fornecedores_atuais": fornecedores_atuais,
        "fornecedores_novos": fornecedores_novos,
        "localizacao_atual": localizacao_atual if not localizacao_ausente else "NÃO INFORMADA",
        "localizacao_nova": localizacao_nova,
        "divergencias": divergencias,
        "tipos_divergencia": {
            "valor_atipico": valor_atipico,
            "fornecedor_novo": fornecedor_novo,
            "localizacao_nova_ou_ausente": localizacao_nova,
        },
        "contatos_aprovadores": empresa.get("contatos", []),
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool 4: enviar_solicitacao_aprovacao
# ---------------------------------------------------------------------------
@server.tool()
def enviar_solicitacao_aprovacao(
    empresa_nome: str,
    pedido_id: str,
    valor_total_atual: float,
    media_historica_mensal: float,
    variacao_percentual: float,
    fornecedores_novos: list[str],
    localizacao_atual: str,
    divergencias: list[str],
    nome_aprovador_1: str,
    email_aprovador_1: str,
    cargo_aprovador_1: str,
    telefone_aprovador_1: str,
    nome_aprovador_2: str,
    email_aprovador_2: str,
    cargo_aprovador_2: str,
    telefone_aprovador_2: str,
) -> str:
    """Gera formalmente a solicitação de aprovação para os 2 contatos responsáveis
    quando divergências são detectadas em uma transação.

    Deve ser chamada apenas quando verificar_conformidade() retornar requer_aprovacao=true.
    Os dados dos aprovadores (nome, email, cargo, telefone) estão disponíveis no campo
    'contatos_aprovadores' do resultado de verificar_conformidade().

    Retorna um relatório completo com os modelos de e-mail prontos para envio imediato.
    """
    divergencias_fmt = (
        "\n".join(f"  • {d}" for d in divergencias)
        if divergencias
        else "  • Divergência identificada"
    )
    assunto = (
        f"[CONFORMIDADE — APROVAÇÃO NECESSÁRIA] "
        f"Divergência detectada — {empresa_nome} / {pedido_id}"
    )

    valor_linha = (
        f"R$ {valor_total_atual:,.2f} (+{variacao_percentual:.1f}% acima da média "
        f"R$ {media_historica_mensal:,.2f})"
        if variacao_percentual > 0
        else f"R$ {valor_total_atual:,.2f}"
    )

    loc_linha = (
        "⚠️ NÃO INFORMADA"
        if not localizacao_atual or localizacao_atual == "NÃO INFORMADA"
        else localizacao_atual
    )

    fornecedores_bloco = ""
    if fornecedores_novos:
        fornecedores_bloco = (
            "\n  Fornecedor(es) NÃO encontrado(s) no histórico:\n"
            + "\n".join(f"    ⚠️ {f}" for f in fornecedores_novos)
        )

    def _email(nome: str, email: str) -> str:
        return (
            f"┌─────────────────────────────────────────────────────────────────┐\n"
            f"  SOLICITAÇÃO DE APROVAÇÃO — {nome.upper()}\n"
            f"  Para: {email}\n"
            f"├─────────────────────────────────────────────────────────────────┤\n"
            f"  Assunto: {assunto}\n\n"
            f"  Prezado(a) {nome},\n\n"
            f"  O sistema de Conformidade de Compras identificou divergências na\n"
            f"  transação abaixo que requerem sua aprovação formal:\n\n"
            f"    • Empresa    : {empresa_nome}\n"
            f"    • Referência : {pedido_id}\n"
            f"    • Valor      : {valor_linha}\n"
            f"    • Localização: {loc_linha}{fornecedores_bloco}\n\n"
            f"  Divergências identificadas:\n"
            f"{divergencias_fmt.replace('  •', '    -')}\n\n"
            f"  Por favor, responda a este e-mail com:\n"
            f"    ✅ APROVADO — informe a justificativa para prosseguir.\n"
            f"    ❌ REJEITADO — a ordem de compra será cancelada automaticamente.\n\n"
            f"  Prazo para resposta: 48 horas a partir do recebimento deste e-mail.\n\n"
            f"  Atenciosamente,\n"
            f"  Sistema de Conformidade de Compras — Agente de Conformidade VF\n"
            f"└─────────────────────────────────────────────────────────────────┘"
        )

    email_1 = _email(nome_aprovador_1, email_aprovador_1)
    email_2 = _email(nome_aprovador_2, email_aprovador_2)

    return (
        f"SOLICITAÇÃO DE APROVAÇÃO ENVIADA\n"
        f"═══════════════════════════════════════════════════════════════\n"
        f"EMPRESA        : {empresa_nome}\n"
        f"PEDIDO/REF.    : {pedido_id}\n"
        f"VALOR ATUAL    : R$ {valor_total_atual:,.2f}\n"
        f"MÉDIA HISTÓRICA: R$ {media_historica_mensal:,.2f}\n"
        f"VARIAÇÃO       : {variacao_percentual:.1f}%\n"
        f"LOCALIZAÇÃO    : {loc_linha}\n\n"
        f"DIVERGÊNCIAS QUE MOTIVARAM O ENVIO:\n"
        f"{divergencias_fmt}\n\n"
        f"CONTATOS ACIONADOS:\n"
        f"- Contato 1: {nome_aprovador_1} ({cargo_aprovador_1})\n"
        f"  E-mail: {email_aprovador_1} | Tel: {telefone_aprovador_1}\n"
        f"  Status: Pendente de Resposta\n\n"
        f"- Contato 2: {nome_aprovador_2} ({cargo_aprovador_2})\n"
        f"  E-mail: {email_aprovador_2} | Tel: {telefone_aprovador_2}\n"
        f"  Status: Pendente de Resposta\n\n"
        f"─────────────────────────────────────────────────────────────────────\n"
        f"MODELOS DE E-MAIL GERADOS PARA ENVIO\n"
        f"─────────────────────────────────────────────────────────────────────\n\n"
        f"{email_1}\n\n"
        f"{email_2}"
    )


# ---------------------------------------------------------------------------
# Tool 5: analisar_lote_csv
# ---------------------------------------------------------------------------
@server.tool()
def analisar_lote_csv(caminho_csv: str) -> str:
    """Ingere um arquivo CSV de transações de compras e executa a verificação de
    conformidade para cada linha automaticamente, consultando o histórico da
    knowledge base internamente.

    Formato esperado do CSV (separador vírgula, cabeçalho obrigatório):
      empresa_id, pedido_id, valor_total, fornecedores, localizacao

    O campo 'fornecedores' pode conter múltiplos valores separados por '|'.
    Exemplo de linha:
      EMP-001,Novembro/2026,4750.00,"Amazon Web Services (AWS)|Google Cloud",São Paulo SP

    Retorna um relatório consolidado com:
      - Resumo: total de transações, quantas aprovadas, quantas com divergências
      - Detalhe por empresa: critérios violados, fornecedores novos, variação percentual
      - Lista de aprovadores a acionar por empresa com divergência

    Args:
        caminho_csv: Caminho absoluto ou relativo ao arquivo CSV. Caminhos relativos
                     são resolvidos a partir da raiz do repositório.
    """
    # Resolve o caminho
    path = Path(caminho_csv)
    if not path.is_absolute():
        path = ROOT / caminho_csv
    if not path.exists():
        # Tenta também relativo ao diretório mcp/dados/
        path_dados = ROOT / "mcp" / "dados" / caminho_csv
        if path_dados.exists():
            path = path_dados
        else:
            return json.dumps({
                "erro": f"Arquivo não encontrado: {caminho_csv}",
                "dica": "Use o caminho completo ou coloque o arquivo em mcp/dados/",
            }, ensure_ascii=False, indent=2)

    # Lê o CSV
    transacoes = []
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transacoes.append({
                    "empresa_id": row["empresa_id"].strip(),
                    "pedido_id": row["pedido_id"].strip(),
                    "valor_total": float(row["valor_total"].strip()),
                    "fornecedores": [f.strip() for f in row["fornecedores"].split("|")],
                    "localizacao": row["localizacao"].strip(),
                })
    except Exception as e:
        return json.dumps({"erro": f"Erro ao ler CSV: {e}"}, ensure_ascii=False, indent=2)

    if not transacoes:
        return json.dumps({"erro": "CSV vazio ou sem linhas de dados."}, ensure_ascii=False, indent=2)

    # Verifica cada transação reutilizando a lógica de verificar_conformidade
    resultados = []
    requerem_aprovacao = []

    for t in transacoes:
        resultado_json = verificar_conformidade(
            empresa_id=t["empresa_id"],
            pedido_id=t["pedido_id"],
            valor_total_atual=t["valor_total"],
            fornecedores_atuais=t["fornecedores"],
            localizacao_atual=t["localizacao"],
        )
        resultado = json.loads(resultado_json)
        resultados.append(resultado)
        if resultado.get("requer_aprovacao"):
            requerem_aprovacao.append(resultado)

    # Monta o relatório consolidado
    total = len(resultados)
    n_ok = total - len(requerem_aprovacao)
    n_nok = len(requerem_aprovacao)

    linhas = [
        f"RELATÓRIO DE CONFORMIDADE — LOTE CSV",
        f"Arquivo : {path.name}",
        f"Total   : {total} transações analisadas",
        f"✅ Em conformidade  : {n_ok}",
        f"⚠️  Requerem aprovação: {n_nok}",
        f"═══════════════════════════════════════════════════════════════",
    ]

    for r in resultados:
        status = "⚠️  REQUER APROVAÇÃO" if r.get("requer_aprovacao") else "✅ EM CONFORMIDADE"
        linhas.append(f"\n{status} — {r.get('empresa_nome', r.get('empresa_id'))} / {r.get('pedido_id')}")
        if r.get("erro"):
            linhas.append(f"  ERRO: {r['erro']}")
            continue
        linhas.append(f"  Valor: R$ {r['valor_total_atual']:,.2f}  |  Média histórica: R$ {r['media_historica_mensal']:,.2f}  |  Variação: {r['variacao_percentual']:+.1f}%")
        if r.get("requer_aprovacao"):
            for div in r.get("divergencias", []):
                linhas.append(f"  • {div}")
            contatos = r.get("contatos_aprovadores", [])
            if contatos:
                linhas.append(f"  Aprovadores a acionar:")
                for c in contatos:
                    linhas.append(f"    → {c['nome']} ({c['area']}) — {c['email']}")

    linhas.append(f"\n═══════════════════════════════════════════════════════════════")
    if requerem_aprovacao:
        linhas.append(f"PRÓXIMO PASSO: chame enviar_solicitacao_aprovacao() para cada")
        linhas.append(f"empresa acima marcada com ⚠️, usando os dados dos aprovadores listados.")
    else:
        linhas.append("Todas as transações estão em conformidade. Nenhuma ação necessária.")

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Tool 6: analisar_lote_csv_json
# ---------------------------------------------------------------------------
@server.tool()
def analisar_lote_csv_json(caminho_csv: str) -> str:
    """Ingere um arquivo CSV de transações de compras e executa a verificação de
    conformidade para cada linha em paralelo (ThreadPoolExecutor), retornando
    structured JSON output pronto para consumo por outros sistemas ou agentes.

    Idêntico a analisar_lote_csv(), mas retorna JSON estruturado em vez de
    relatório em texto — adequado para trigger-based workflows e integrações.

    Formato esperado do CSV (separador vírgula, cabeçalho obrigatório):
      empresa_id, pedido_id, valor_total, fornecedores, localizacao

    O campo 'fornecedores' pode conter múltiplos valores separados por '|'.

    Retorna JSON com:
      - resumo: { total, em_conformidade, requerem_aprovacao }
      - resultados: lista completa de verificações com todos os campos
      - acoes_necessarias: lista apenas das empresas que requerem aprovação,
        com contatos_aprovadores prontos para enviar_solicitacao_aprovacao()

    Args:
        caminho_csv: Caminho absoluto ou relativo ao arquivo CSV. Caminhos relativos
                     são resolvidos a partir da raiz do repositório.
    """
    import concurrent.futures

    # Resolve o caminho
    path = Path(caminho_csv)
    if not path.is_absolute():
        path = ROOT / caminho_csv
    if not path.exists():
        path_dados = ROOT / "mcp" / "dados" / caminho_csv
        if path_dados.exists():
            path = path_dados
        else:
            return json.dumps({
                "erro": f"Arquivo não encontrado: {caminho_csv}",
                "dica": "Use o caminho completo ou coloque o arquivo em mcp/dados/",
            }, ensure_ascii=False, indent=2)

    # Lê o CSV
    transacoes = []
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transacoes.append({
                    "empresa_id": row["empresa_id"].strip(),
                    "pedido_id": row["pedido_id"].strip(),
                    "valor_total": float(row["valor_total"].strip()),
                    "fornecedores": [f.strip() for f in row["fornecedores"].split("|")],
                    "localizacao": row["localizacao"].strip(),
                })
    except Exception as e:
        return json.dumps({"erro": f"Erro ao ler CSV: {e}"}, ensure_ascii=False, indent=2)

    if not transacoes:
        return json.dumps({"erro": "CSV vazio ou sem linhas de dados."}, ensure_ascii=False, indent=2)

    # Verifica cada transação em paralelo — cada worker é um sub-agente de auditoria
    def _verificar(t: dict) -> dict:
        resultado_json = verificar_conformidade(
            empresa_id=t["empresa_id"],
            pedido_id=t["pedido_id"],
            valor_total_atual=t["valor_total"],
            fornecedores_atuais=t["fornecedores"],
            localizacao_atual=t["localizacao"],
        )
        return json.loads(resultado_json)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(transacoes)) as executor:
        resultados = list(executor.map(_verificar, transacoes))

    acoes_necessarias = [r for r in resultados if r.get("requer_aprovacao")]

    return json.dumps({
        "arquivo": path.name,
        "resumo": {
            "total_transacoes": len(resultados),
            "em_conformidade": len(resultados) - len(acoes_necessarias),
            "requerem_aprovacao": len(acoes_necessarias),
            "workers_paralelos": len(transacoes),
        },
        "resultados": resultados,
        "acoes_necessarias": [
            {
                "empresa_nome": r["empresa_nome"],
                "empresa_id": r["empresa_id"],
                "pedido_id": r["pedido_id"],
                "divergencias": r["divergencias"],
                "contatos_aprovadores": r["contatos_aprovadores"],
            }
            for r in acoes_necessarias
        ],
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    server.run(transport="stdio")
