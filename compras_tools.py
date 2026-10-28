from ibm_watsonx_orchestrate.agent_builder.tools import tool
import json


@tool
def auditar_compras(registros_json: str) -> str:
    """Analisa registros de compras unitários e identifica transações incoerentes
    por preço ou por ausência de localização de origem da compra.

    Critérios de incoerência:
    - Valor unitário > 15% acima da média histórica do mesmo item.
    - Campo 'localizacao' ausente, vazio ou nulo no registro.

    Args:
        registros_json (str): JSON com lista de registros de compra. Cada registro
            deve conter: pedido_id, item, fornecedor, valor_unitario,
            media_historica e localizacao.

    Returns:
        str: Relatório JSON com as transações incoerentes identificadas, incluindo
             o motivo específico de cada divergência.
    """
    registros = json.loads(registros_json)
    incoerentes = []

    for r in registros:
        motivos = []

        # --- Validação de preço ---
        valor = float(r.get("valor_unitario", 0))
        media = float(r.get("media_historica", 0))
        variacao = 0.0
        if media > 0:
            variacao = ((valor - media) / media) * 100
            if variacao > 15:
                motivos.append(
                    f"Valor unitário R${valor:.2f} está {variacao:.1f}% acima "
                    f"da média histórica R${media:.2f}"
                )

        # --- Validação de localização ---
        localizacao = r.get("localizacao", "")
        localizacao_ausente = not localizacao or str(localizacao).strip() == ""
        if localizacao_ausente:
            motivos.append(
                "Localização de origem da compra não informada no registro"
            )

        if motivos:
            incoerentes.append({
                "pedido_id": r.get("pedido_id"),
                "item": r.get("item"),
                "fornecedor": r.get("fornecedor"),
                "valor_atual": valor,
                "media_historica": media,
                "variacao_percentual": round(variacao, 2),
                "localizacao": localizacao if not localizacao_ausente else "NÃO INFORMADA",
                "motivos": motivos,
                "tipos_divergencia": {
                    "preco_incoerente": variacao > 15,
                    "localizacao_ausente": localizacao_ausente,
                },
            })

    return json.dumps({
        "total_analisado": len(registros),
        "total_incoerentes": len(incoerentes),
        "transacoes_incoerentes": incoerentes,
    }, ensure_ascii=False, indent=2)


@tool
def auditar_historico_mensal_empresa(empresa_json: str) -> str:
    """Analisa o histórico mensal de compras de uma empresa corporativa e identifica
    meses com divergências de valor, localização ausente, fornecedores novos ou
    itens nunca comprados anteriormente.

    A média de referência é calculada via leave-one-out (média dos outros meses).
    Fornecedores e itens são comparados contra o conjunto histórico da própria empresa:
    qualquer fornecedor ou item que não apareça em NENHUM outro mês é sinalizado.

    Critérios de incoerência:
    - Valor total mensal > 15% acima da média dos outros meses da mesma empresa.
    - Campo 'localizacao' ausente, vazio ou nulo no registro mensal.
    - Fornecedor presente no mês que nunca apareceu em nenhum outro mês do histórico.
    - Item comprado no mês que nunca apareceu em nenhum outro mês do histórico.

    Args:
        empresa_json (str): JSON de uma única empresa no formato do documento
            'empresas_corporativas.json', contendo os campos 'id', 'nome',
            'contatos' e 'historico_mensal'.

    Returns:
        str: Relatório JSON com divergências identificadas, contatos da empresa
             e resumo por mês analisado.
    """
    empresa = json.loads(empresa_json)
    nome_empresa = empresa.get("nome", "Desconhecida")
    empresa_id = empresa.get("id", "N/A")
    historico = empresa.get("historico_mensal", [])
    contatos = empresa.get("contatos", [])

    valores = [float(m.get("valor_total", 0)) for m in historico]

    # Conjuntos históricos globais por empresa (todos os meses)
    todos_fornecedores = set()
    todos_itens = set()
    for m in historico:
        for f in m.get("fornecedores", []):
            todos_fornecedores.add(f.strip().lower())
        for it in m.get("itens", []):
            todos_itens.add(it.get("descricao", "").strip().lower())

    divergencias = []

    for i, mes in enumerate(historico):
        motivos = []
        valor = float(mes.get("valor_total", 0))

        # --- Validação de valor (leave-one-out) ---
        outros_valores = [v for j, v in enumerate(valores) if j != i]
        media = sum(outros_valores) / len(outros_valores) if outros_valores else 0.0
        variacao = ((valor - media) / media * 100) if media > 0 else 0.0
        if variacao > 15:
            motivos.append(
                f"Valor total R${valor:,.2f} está {variacao:.1f}% acima da média "
                f"dos demais meses R${media:,.2f}"
            )

        # --- Validação de localização ---
        localizacao = mes.get("localizacao", "")
        localizacao_ausente = not localizacao or str(localizacao).strip() == ""
        if localizacao_ausente:
            motivos.append("Localização de origem da compra não informada neste mês")

        # Conjuntos dos OUTROS meses (excluindo o mês atual) para comparação
        outros_fornecedores = set()
        outros_itens = set()
        for j, outro in enumerate(historico):
            if j == i:
                continue
            for f in outro.get("fornecedores", []):
                outros_fornecedores.add(f.strip().lower())
            for it in outro.get("itens", []):
                outros_itens.add(it.get("descricao", "").strip().lower())

        # --- Validação de fornecedores novos ---
        fornecedores_mes = mes.get("fornecedores", [])
        fornecedores_novos = [
            f for f in fornecedores_mes
            if f.strip().lower() not in outros_fornecedores
        ]
        if fornecedores_novos:
            motivos.append(
                f"Fornecedor(es) nunca utilizado(s) anteriormente nesta empresa: "
                f"{', '.join(fornecedores_novos)}"
            )

        # --- Validação de itens novos ---
        itens_mes = mes.get("itens", [])
        itens_novos = [
            it["descricao"] for it in itens_mes
            if it.get("descricao", "").strip().lower() not in outros_itens
        ]
        if itens_novos:
            motivos.append(
                f"Item(ns) nunca comprado(s) anteriormente nesta empresa: "
                f"{', '.join(itens_novos)}"
            )

        if motivos:
            divergencias.append({
                "mes": mes.get("mes"),
                "valor_total": valor,
                "media_referencia": round(media, 2),
                "variacao_percentual": round(variacao, 2),
                "localizacao": localizacao if not localizacao_ausente else "NÃO INFORMADA",
                "fornecedores": fornecedores_mes,
                "fornecedores_novos": fornecedores_novos,
                "itens": itens_mes,
                "itens_novos": itens_novos,
                "motivos": motivos,
                "tipos_divergencia": {
                    "valor_atipico": variacao > 15,
                    "localizacao_ausente": localizacao_ausente,
                    "fornecedor_novo": len(fornecedores_novos) > 0,
                    "item_novo": len(itens_novos) > 0,
                },
            })

    return json.dumps({
        "empresa_id": empresa_id,
        "empresa_nome": nome_empresa,
        "total_meses_analisados": len(historico),
        "total_meses_com_divergencia": len(divergencias),
        "fornecedores_historicos": sorted(todos_fornecedores),
        "itens_historicos": sorted(todos_itens),
        "contatos": contatos,
        "divergencias": divergencias,
    }, ensure_ascii=False, indent=2)


@tool
def gerar_notificacao_aprovador(
    nome_aprovador: str,
    empresa_nome: str,
    pedido_id: str,
    item: str,
    fornecedor: str,
    valor_atual: float,
    media_historica: float,
    variacao_percentual: float,
    localizacao: str,
    motivos_json: str,
    fornecedores_novos_json: str = "[]",
    itens_novos_json: str = "[]",
) -> str:
    """Gera o texto formatado da notificação de solicitação de confirmação de compra,
    contemplando divergências de preço, localização ausente, fornecedor novo e/ou item novo.

    Args:
        nome_aprovador (str): Nome completo do aprovador a ser acionado.
        empresa_nome (str): Nome da empresa à qual a compra pertence.
        pedido_id (str): Código/ID do pedido ou mês de referência com divergência.
        item (str): Nome do item, serviço ou período com incoerência.
        fornecedor (str): Nome do(s) fornecedor(es) da compra.
        valor_atual (float): Valor atual da compra (unitário ou total mensal).
        media_historica (float): Média histórica de referência (0 se não aplicável).
        variacao_percentual (float): Percentual de variação acima da média (0 se não aplicável).
        localizacao (str): Localização registrada ou "NÃO INFORMADA".
        motivos_json (str): JSON com lista de strings descrevendo cada motivo de retenção.
        fornecedores_novos_json (str): JSON com lista de fornecedores nunca usados antes. Default "[]".
        itens_novos_json (str): JSON com lista de itens nunca comprados antes. Default "[]".

    Returns:
        str: Texto completo da notificação formatada.
    """
    motivos: list = json.loads(motivos_json)
    motivos_fmt = "\n".join(f"  • {m}" for m in motivos)

    fornecedores_novos: list = json.loads(fornecedores_novos_json)
    itens_novos: list = json.loads(itens_novos_json)

    localizacao_linha = (
        f"- **Localização da Compra:** {localizacao}"
        if localizacao and localizacao != "NÃO INFORMADA"
        else "- **Localização da Compra:** ⚠️ NÃO INFORMADA"
    )

    variacao_linha = (
        f"- **Valor:** R$ {valor_atual:,.2f} "
        f"(Média de Referência: R$ {media_historica:,.2f} — Variação: +{variacao_percentual:.1f}%)"
        if variacao_percentual > 0
        else f"- **Valor:** R$ {valor_atual:,.2f}"
    )

    novidades_bloco = ""
    if fornecedores_novos:
        lista = ", ".join(fornecedores_novos)
        novidades_bloco += f"\n- **Fornecedor(es) NÃO encontrado(s) no histórico:** ⚠️ {lista}"
    if itens_novos:
        lista = ", ".join(itens_novos)
        novidades_bloco += f"\n- **Item(ns) NÃO encontrado(s) no histórico:** ⚠️ {lista}"

    notificacao = f"""
[SOLICITAÇÃO DE CONFIRMAÇÃO DE COMPRA - DIVERGÊNCIA DETECTADA]

Olá, {nome_aprovador}!

Identificamos incoerência(s) na seguinte compra de **{empresa_nome}** que requer(em) sua aprovação formal:

- **Pedido/Referência:** {pedido_id}
- **Item/Período:** {item}
- **Fornecedor(es):** {fornecedor}
{variacao_linha}
{localizacao_linha}{novidades_bloco}

**Motivo(s) da Retenção:**
{motivos_fmt}

⚠️ Ação necessária: Responda a esta mensagem informando "APROVADO" com a justificativa,
ou "REJEITADO" para cancelar a ordem de compra.
""".strip()

    return notificacao


@tool
def registrar_status_aprovacao(
    empresa_nome: str,
    pedido_id: str,
    aprovador_1_nome: str,
    aprovador_1_cargo: str,
    aprovador_1_status: str,
    aprovador_2_nome: str,
    aprovador_2_cargo: str,
    aprovador_2_status: str,
    tipos_divergencia_json: str,
) -> str:
    """Registra e consolida o status final de aprovação de uma transação com divergência.

    Determina o STATUS DA OPERAÇÃO com base nas respostas dos 2 aprovadores:
    - Aprovado: ambos confirmaram com status "Confirmado".
    - Rejeitado: pelo menos um respondeu "Rejeitado".
    - Pendente de Confirmação: algum aprovador ainda não respondeu.

    Args:
        empresa_nome (str): Nome da empresa à qual a compra pertence.
        pedido_id (str): Código/ID do pedido ou mês de referência.
        aprovador_1_nome (str): Nome completo do primeiro aprovador.
        aprovador_1_cargo (str): Cargo/Área do primeiro aprovador.
        aprovador_1_status (str): "Confirmado", "Rejeitado" ou "Pendente".
        aprovador_2_nome (str): Nome completo do segundo aprovador.
        aprovador_2_cargo (str): Cargo/Área do segundo aprovador.
        aprovador_2_status (str): "Confirmado", "Rejeitado" ou "Pendente".
        tipos_divergencia_json (str): JSON com flags indicando os tipos de divergência.
            Exemplo: {"valor_atipico": true, "localizacao_ausente": true,
                      "preco_incoerente": false}

    Returns:
        str: Relatório final formatado com empresa, status da operação,
             tipos de divergência e contatos acionados nominalmente.
    """
    statuses = [aprovador_1_status, aprovador_2_status]

    if "Rejeitado" in statuses:
        status_operacao = "Rejeitado"
    elif all(s == "Confirmado" for s in statuses):
        status_operacao = "Aprovado"
    else:
        status_operacao = "Pendente de Confirmação"

    tipos: dict = json.loads(tipos_divergencia_json)
    divergencias = []
    if tipos.get("preco_incoerente") or tipos.get("valor_atipico"):
        divergencias.append("Valor > 15% acima da média histórica/referência")
    if tipos.get("localizacao_ausente"):
        divergencias.append("Localização de origem não informada")
    if tipos.get("fornecedor_novo"):
        divergencias.append("Fornecedor nunca utilizado anteriormente nesta empresa")
    if tipos.get("item_novo"):
        divergencias.append("Item nunca comprado anteriormente nesta empresa")
    divergencias_fmt = (
        "\n".join(f"  • {d}" for d in divergencias)
        if divergencias
        else "  • Não especificado"
    )

    relatorio = f"""
STATUS DA OPERAÇÃO: {status_operacao}
EMPRESA: {empresa_nome}
PEDIDO/REFERÊNCIA: {pedido_id}

TIPOS DE DIVERGÊNCIA IDENTIFICADOS:
{divergencias_fmt}

CONTATOS ACIONADOS PARA VALIDAÇÃO:
- Contato 1: {aprovador_1_nome} ({aprovador_1_cargo}) - Status: {aprovador_1_status}
- Contato 2: {aprovador_2_nome} ({aprovador_2_cargo}) - Status: {aprovador_2_status}
""".strip()

    return relatorio
