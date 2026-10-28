from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import List
import json


@tool
def auditar_compras(registros_json: str) -> str:
    """Analisa registros de compras e identifica transações com valores incoerentes ou localização ausente.

    Considera INCOERENTE quando:
    - O valor unitário da compra for > 15% acima da média histórica praticada para o mesmo item.
    - O campo localização de origem da compra estiver ausente ou vazio.

    Args:
        registros_json (str): JSON com lista de registros de compra. Cada registro
            deve conter: pedido_id, item, fornecedor, valor_unitario, media_historica, localizacao (opcional).

    Returns:
        str: Relatório JSON com as transações incoerentes identificadas.
    """
    registros = json.loads(registros_json)
    incoerentes = []

    for r in registros:
        valor = float(r.get("valor_unitario", 0))
        media = float(r.get("media_historica", 0))
        localizacao = r.get("localizacao")
        motivos = []

        # Validação de preço (> 15% da média)
        if media > 0:
            variacao = ((valor - media) / media) * 100
            if variacao > 15:
                motivos.append(
                    f"Valor unitário R${valor:.2f} está {variacao:.1f}% acima da média histórica R${media:.2f}"
                )
        else:
            variacao = 0.0

        # Validação de localização
        localizacao_ausente = not localizacao or str(localizacao).strip() == ""
        if localizacao_ausente:
            motivos.append("Localização de origem da compra não informada no registro")

        if motivos:
            incoerentes.append({
                "pedido_id": r.get("pedido_id"),
                "item": r.get("item"),
                "fornecedor": r.get("fornecedor"),
                "valor_atual": valor,
                "media_historica": media,
                "variacao_percentual": round(variacao, 2),
                "localizacao": localizacao if not localizacao_ausente else "NÃO INFORMADA",
                "motivos": motivos
            })

    return json.dumps({
        "total_analisado": len(registros),
        "total_incoerentes": len(incoerentes),
        "transacoes_incoerentes": incoerentes
    }, ensure_ascii=False, indent=2)


@tool
def gerar_notificacao_aprovador(
    nome_aprovador: str,
    pedido_id: str,
    item: str,
    fornecedor: str,
    valor_atual: float,
    media_historica: float,
    variacao_percentual: float,
    motivo: str
) -> str:
    """Gera o texto formatado da notificação de solicitação de confirmação de compra.

    Args:
        nome_aprovador (str): Nome completo do aprovador a ser acionado.
        pedido_id (str): Código/ID do pedido com divergência.
        item (str): Nome do item ou serviço com preço incoerente.
        fornecedor (str): Nome do fornecedor da compra.
        valor_atual (float): Valor unitário atual da compra.
        media_historica (float): Média histórica de preço para o item.
        variacao_percentual (float): Percentual de variação acima da média.
        motivo (str): Descrição curta do motivo da retenção.

    Returns:
        str: Texto completo da notificação formatada.
    """
    notificacao = f"""
[SOLICITAÇÃO DE CONFIRMAÇÃO DE COMPRA - DIVERGÊNCIA DETECTADA]

Olá, {nome_aprovador}!

Identificamos uma incoerência na seguinte compra que requer sua aprovação formal:

- Pedido/ID: {pedido_id}
- Item/Serviço: {item}
- Fornecedor: {fornecedor}
- Valor Atual: R$ {valor_atual:.2f} (Média Histórica: R$ {media_historica:.2f} - Variação: +{variacao_percentual:.1f}%)
- Motivo da Retenção: {motivo}

⚠️ Ação necessária: Responda a esta mensagem informando "APROVADO" com a justificativa,
ou "REJEITADO" para cancelar a ordem de compra.
""".strip()
    return notificacao


@tool
def registrar_status_aprovacao(
    pedido_id: str,
    aprovador_1_nome: str,
    aprovador_1_cargo: str,
    aprovador_1_status: str,
    aprovador_2_nome: str,
    aprovador_2_cargo: str,
    aprovador_2_status: str
) -> str:
    """Registra o status final de aprovação de uma transação com divergência.

    Determina o STATUS DA OPERAÇÃO com base nas respostas dos 2 aprovadores:
    - Aprovado: ambos confirmaram com "APROVADO"
    - Rejeitado: pelo menos um respondeu "REJEITADO"
    - Pendente de Confirmação: algum aprovador ainda não respondeu

    Args:
        pedido_id (str): Código/ID do pedido.
        aprovador_1_nome (str): Nome completo do primeiro aprovador.
        aprovador_1_cargo (str): Cargo/Área do primeiro aprovador.
        aprovador_1_status (str): Status do primeiro aprovador: "Confirmado", "Rejeitado" ou "Pendente".
        aprovador_2_nome (str): Nome completo do segundo aprovador.
        aprovador_2_cargo (str): Cargo/Área do segundo aprovador.
        aprovador_2_status (str): Status do segundo aprovador: "Confirmado", "Rejeitado" ou "Pendente".

    Returns:
        str: Relatório final formatado com status da operação e contatos acionados.
    """
    statuses = [aprovador_1_status, aprovador_2_status]

    if "Rejeitado" in statuses:
        status_operacao = "Rejeitado"
    elif all(s == "Confirmado" for s in statuses):
        status_operacao = "Aprovado"
    else:
        status_operacao = "Pendente de Confirmação"

    relatorio = f"""
STATUS DA OPERAÇÃO: {status_operacao}
PEDIDO: {pedido_id}

CONTATOS ACIONADOS PARA VALIDAÇÃO:
- Contato 1: {aprovador_1_nome} ({aprovador_1_cargo}) - Status: {aprovador_1_status}
- Contato 2: {aprovador_2_nome} ({aprovador_2_cargo}) - Status: {aprovador_2_status}
""".strip()
    return relatorio
