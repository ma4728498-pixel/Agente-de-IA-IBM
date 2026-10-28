from ibm_watsonx_orchestrate.agent_builder.tools import tool
import json

# ---------------------------------------------------------------------------
# Dados das empresas embutidos diretamente (sem RAG / knowledge base)
# ---------------------------------------------------------------------------
_EMPRESAS = [
    {
        "id": "EMP-001",
        "nome": "Alpha Tech Soluções S.A.",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Carla Menezes", "area": "Financeiro/Compras", "email": "carla.menezes@alphatech.com", "telefone": "(11) 98765-1234"},
            {"tipo": "Pessoa de Confiança", "nome": "Roberto Siqueira", "area": "Diretor de Tecnologia", "email": "roberto.siqueira@alphatech.com", "telefone": "(11) 98765-5678"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 4520.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "Kalunga"], "itens": [{"descricao": "Servidores AWS", "valor": 3200.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "Papelaria", "valor": 320.00}]},
            {"mes": "Junho/2026", "valor_total": 4490.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "Cirilo Cabos"], "itens": [{"descricao": "Servidores AWS", "valor": 3200.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "Cabos UTP", "valor": 290.00}]},
            {"mes": "Julho/2026", "valor_total": 4850.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "Logitech Brasil"], "itens": [{"descricao": "Servidores AWS", "valor": 3200.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "Kits Teclado/Mouse", "valor": 650.00}]},
            {"mes": "Agosto/2026", "valor_total": 4510.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "HP Inc."], "itens": [{"descricao": "Servidores AWS", "valor": 3200.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "Toners HP", "valor": 310.00}]},
            {"mes": "Setembro/2026", "valor_total": 5120.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "JetBrains s.r.o."], "itens": [{"descricao": "Servidores AWS", "valor": 3500.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "JetBrains", "valor": 620.00}]},
            {"mes": "Outubro/2026", "valor_total": 4530.00, "localizacao": "São Paulo, SP", "fornecedores": ["Amazon Web Services (AWS)", "Google Cloud", "Fast Shop"], "itens": [{"descricao": "Servidores AWS", "valor": 3200.00}, {"descricao": "Google Workspace", "valor": 1000.00}, {"descricao": "Conectores", "valor": 330.00}]},
        ],
    },
    {
        "id": "EMP-002",
        "nome": "Beta Logística e Transportes Ltda",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Marcos Vinícius", "area": "Gestão de Frota", "email": "marcos.vinicius@betalogistica.com", "telefone": "(11) 97654-1111"},
            {"tipo": "Pessoa de Confiança", "nome": "Juliano Antunes", "area": "Gerente de Operações", "email": "juliano.antunes@betalogistica.com", "telefone": "(11) 97654-2222"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 12400.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Petrobras Distribuidora"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 11200.00}, {"descricao": "Arla 32", "valor": 1200.00}]},
            {"mes": "Junho/2026", "valor_total": 11900.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Petrobras Distribuidora"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 10700.00}, {"descricao": "Arla 32", "valor": 1200.00}]},
            {"mes": "Julho/2026", "valor_total": 14200.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Michelin do Brasil"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 10100.00}, {"descricao": "Pneu Michelin", "valor": 4100.00}]},
            {"mes": "Agosto/2026", "valor_total": 12150.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Petrobras Distribuidora"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 10950.00}, {"descricao": "Arla 32", "valor": 1200.00}]},
            {"mes": "Setembro/2026", "valor_total": 12300.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Petrobras Distribuidora"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 11050.00}, {"descricao": "Arla 32", "valor": 1250.00}]},
            {"mes": "Outubro/2026", "valor_total": 13800.00, "localizacao": "Campinas, SP", "fornecedores": ["Auto Posto Rodovia", "Fras-le Autopeças"], "itens": [{"descricao": "Óleo Diesel S10", "valor": 10600.00}, {"descricao": "Pastilhas de Freio", "valor": 3200.00}]},
        ],
    },
    {
        "id": "EMP-003",
        "nome": "Gama Materiais de Construção Eireli",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Luciana Prado", "area": "Almoxarifado e Faturamento", "email": "luciana.prado@gamamateriais.com", "telefone": "(19) 98888-3333"},
            {"tipo": "Pessoa de Confiança", "nome": "Eduardo Gama", "area": "Sócio Proprietário", "email": "eduardo.gama@gamamateriais.com", "telefone": "(19) 98888-4444"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 22500.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A."], "itens": [{"descricao": "100 Paletes de Cimento CP II Z-32", "valor": 22500.00}]},
            {"mes": "Junho/2026", "valor_total": 21800.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A."], "itens": [{"descricao": "95 Paletes de Cimento CP II Z-32", "valor": 21800.00}]},
            {"mes": "Julho/2026", "valor_total": 23100.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A.", "Gerdau Aços"], "itens": [{"descricao": "Paletes de Cimento", "valor": 18000.00}, {"descricao": "Vergalhões CA-50", "valor": 5100.00}]},
            {"mes": "Agosto/2026", "valor_total": 22000.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A."], "itens": [{"descricao": "98 Paletes de Cimento CP II Z-32", "valor": 22000.00}]},
            {"mes": "Setembro/2026", "valor_total": 22400.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A."], "itens": [{"descricao": "100 Paletes de Cimento CP II Z-32", "valor": 22400.00}]},
            {"mes": "Outubro/2026", "valor_total": 24600.00, "localizacao": "Limeira, SP", "fornecedores": ["Cimento Votoran S.A.", "Amanco Wavin"], "itens": [{"descricao": "Paletes de Cimento", "valor": 20100.00}, {"descricao": "Tubos PVC Esgoto", "valor": 4500.00}]},
        ],
    },
    {
        "id": "EMP-004",
        "nome": "Delta Alimentos e Bebidas S.A.",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Beatriz Souza", "area": "Contas a Pagar", "email": "beatriz.souza@deltaalimentos.com", "telefone": "(21) 99111-5555"},
            {"tipo": "Pessoa de Confiança", "nome": "Fernando Castilho", "area": "Diretor Industrial", "email": "fernando.castilho@deltaalimentos.com", "telefone": "(21) 99111-6666"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 31200.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 18500.00}, {"descricao": "Óleo de Soja", "valor": 9200.00}, {"descricao": "Embalagens", "valor": 3500.00}]},
            {"mes": "Junho/2026", "valor_total": 30800.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 17900.00}, {"descricao": "Óleo de Soja", "valor": 9200.00}, {"descricao": "Embalagens", "valor": 3700.00}]},
            {"mes": "Julho/2026", "valor_total": 32500.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 19800.00}, {"descricao": "Óleo de Soja", "valor": 9200.00}, {"descricao": "Embalagens", "valor": 3500.00}]},
            {"mes": "Agosto/2026", "valor_total": 31000.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 18500.00}, {"descricao": "Óleo de Soja", "valor": 8900.00}, {"descricao": "Embalagens", "valor": 3600.00}]},
            {"mes": "Setembro/2026", "valor_total": 31900.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 19000.00}, {"descricao": "Óleo de Soja", "valor": 9200.00}, {"descricao": "Embalagens", "valor": 3700.00}]},
            {"mes": "Outubro/2026", "valor_total": 33400.00, "localizacao": "Rio de Janeiro, RJ", "fornecedores": ["Moinho J. Macedo", "Cargill Agrícola", "Tetra Pak"], "itens": [{"descricao": "Farinha de Trigo", "valor": 20100.00}, {"descricao": "Óleo de Soja", "valor": 9500.00}, {"descricao": "Embalagens", "valor": 3800.00}]},
        ],
    },
    {
        "id": "EMP-005",
        "nome": "Épsilon Serviços Digitais Ltda",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Gabriel Nogueira", "area": "Financeiro", "email": "gabriel.nogueira@epsilonservicos.com", "telefone": "(31) 98222-7777"},
            {"tipo": "Pessoa de Confiança", "nome": "Vanessa Duarte", "area": "Head de Engenharia de Software", "email": "vanessa.duarte@epsilonservicos.com", "telefone": "(31) 98222-8888"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 7450.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 3850.00}]},
            {"mes": "Junho/2026", "valor_total": 7520.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 3920.00}]},
            {"mes": "Julho/2026", "valor_total": 8100.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)", "Kalunga"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 3900.00}, {"descricao": "Cabos/Suportes", "valor": 600.00}]},
            {"mes": "Agosto/2026", "valor_total": 7480.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 3880.00}]},
            {"mes": "Setembro/2026", "valor_total": 7600.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 4000.00}]},
            {"mes": "Outubro/2026", "valor_total": 7500.00, "localizacao": "Belo Horizonte, MG", "fornecedores": ["JetBrains s.r.o.", "Amazon Web Services (AWS)"], "itens": [{"descricao": "Licenças JetBrains", "valor": 3600.00}, {"descricao": "Servidores AWS", "valor": 3900.00}]},
        ],
    },
    {
        "id": "EMP-006",
        "nome": "Zeta Vestuário e Moda Ltda",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Simone Ribeiro", "area": "Compras e Suprimentos", "email": "simone.ribeiro@zetamoda.com", "telefone": "(41) 99333-9999"},
            {"tipo": "Pessoa de Confiança", "nome": "Ricardo Mendes", "area": "Diretor Criativo", "email": "ricardo.mendes@zetamoda.com", "telefone": "(41) 99333-0000"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 9250.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Aviamentos Haco"], "itens": [{"descricao": "Rolos de Tecido Algodão", "valor": 6500.00}, {"descricao": "Aviamentos", "valor": 2750.00}]},
            {"mes": "Junho/2026", "valor_total": 9100.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Aviamentos Haco"], "itens": [{"descricao": "Rolos de Tecido Viscose", "valor": 6300.00}, {"descricao": "Aviamentos", "valor": 2800.00}]},
            {"mes": "Julho/2026", "valor_total": 9800.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Aviamentos Haco"], "itens": [{"descricao": "Rolos de Tecido Algodão", "valor": 6900.00}, {"descricao": "Etiquetas e Tags", "valor": 2900.00}]},
            {"mes": "Agosto/2026", "valor_total": 9200.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Aviamentos Haco"], "itens": [{"descricao": "Rolos de Tecido Viscose", "valor": 6350.00}, {"descricao": "Aviamentos", "valor": 2850.00}]},
            {"mes": "Setembro/2026", "valor_total": 9350.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Aviamentos Haco"], "itens": [{"descricao": "Rolos de Tecido Algodão", "valor": 6500.00}, {"descricao": "Aviamentos diversos", "valor": 2850.00}]},
            {"mes": "Outubro/2026", "valor_total": 10150.00, "localizacao": "Curitiba, PR", "fornecedores": ["Têxtil Santa Rita", "Embalagens Âmbar"], "itens": [{"descricao": "Tecidos Coleção Verão", "valor": 7200.00}, {"descricao": "Embalagens/Sacolas", "valor": 2950.00}]},
        ],
    },
    {
        "id": "EMP-007",
        "nome": "Eta Energia Solar e Sustentabilidade",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Tatiana Farias", "area": "Tesouraria", "email": "tatiana.farias@etasolar.com", "telefone": "(61) 98444-1212"},
            {"tipo": "Pessoa de Confiança", "nome": "Marcelo H. Diniz", "area": "Gerente de Projetos de Engenharia", "email": "marcelo.diniz@etasolar.com", "telefone": "(61) 98444-3434"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 48500.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "WEG S.A."], "itens": [{"descricao": "Painéis Solares 550W", "valor": 34000.00}, {"descricao": "Inversores 15kW", "valor": 14500.00}]},
            {"mes": "Junho/2026", "valor_total": 47900.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "WEG S.A."], "itens": [{"descricao": "Painéis Solares 550W", "valor": 34000.00}, {"descricao": "Inversores 15kW", "valor": 13900.00}]},
            {"mes": "Julho/2026", "valor_total": 51200.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "Prysmian Group"], "itens": [{"descricao": "Painéis Solares 550W", "valor": 37400.00}, {"descricao": "Cabos Solares/Conectores", "valor": 13800.00}]},
            {"mes": "Agosto/2026", "valor_total": 48000.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "WEG S.A."], "itens": [{"descricao": "Painéis Solares 550W", "valor": 34000.00}, {"descricao": "Inversores 15kW", "valor": 14000.00}]},
            {"mes": "Setembro/2026", "valor_total": 49100.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "WEG S.A."], "itens": [{"descricao": "Painéis Solares 550W", "valor": 34000.00}, {"descricao": "Inversores 15kW", "valor": 15100.00}]},
            {"mes": "Outubro/2026", "valor_total": 52400.00, "localizacao": "Brasília, DF", "fornecedores": ["Canadian Solar", "Phoenix Contact"], "itens": [{"descricao": "Painéis Solares 550W", "valor": 41000.00}, {"descricao": "String Boxes de Proteção", "valor": 11400.00}]},
        ],
    },
    {
        "id": "EMP-008",
        "nome": "Teta Consultoria Financeira S.A.",
        "contatos": [
            {"tipo": "Administrativo", "nome": "Felipe Cardoso", "area": "Controladoria", "email": "felipe.cardoso@tetaconsultoria.com", "telefone": "(51) 98555-5656"},
            {"tipo": "Pessoa de Confiança", "nome": "Amanda Vasconcelos", "area": "Sócia Sênior", "email": "amanda.vasconcelos@tetaconsultoria.com", "telefone": "(51) 98555-7878"},
        ],
        "historico_mensal": [
            {"mes": "Maio/2026", "valor_total": 6850.00, "localizacao": "Porto Alegre, RS", "fornecedores": ["KPMG Consultoria", "Hewlett-Packard (HP)"], "itens": [{"descricao": "Módulo de Auditoria Contábil", "valor": 5600.00}, {"descricao": "Calculadoras HP 12C", "valor": 1250.00}]},
        ],
    },
]

_EMPRESAS_IDX = {e["id"]: e for e in _EMPRESAS}


# ---------------------------------------------------------------------------
# Ferramentas
# ---------------------------------------------------------------------------

@tool
def listar_empresas() -> str:
    """Lista todas as empresas corporativas disponíveis para auditoria com seus
    respectivos IDs e nomes.

    Returns:
        str: JSON com lista de empresas contendo id e nome.
    """
    resultado = [{"id": e["id"], "nome": e["nome"]} for e in _EMPRESAS]
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def auditar_empresa(empresa_id: str) -> str:
    """Audita o histórico mensal de compras de uma empresa e identifica meses com
    divergências de valor, localização ausente, fornecedores novos ou itens nunca
    comprados anteriormente.

    A média de referência é calculada via leave-one-out (média dos outros meses).
    Fornecedores e itens são comparados contra o conjunto histórico da empresa:
    qualquer fornecedor ou item que não apareça em NENHUM outro mês é sinalizado.

    Critérios de incoerência:
    - Valor total mensal > 15% acima da média dos outros meses da mesma empresa.
    - Campo 'localizacao' ausente, vazio ou nulo no registro mensal.
    - Fornecedor presente no mês que nunca apareceu em nenhum outro mês do histórico.
    - Item comprado no mês que nunca apareceu em nenhum outro mês do histórico.

    Os dados da empresa e seus contatos já estão embutidos na ferramenta.

    Args:
        empresa_id (str): ID da empresa a auditar (ex: "EMP-001"). Use
            `listar_empresas` para obter os IDs disponíveis.

    Returns:
        str: Relatório JSON com divergências identificadas e contatos da empresa.
    """
    empresa = _EMPRESAS_IDX.get(empresa_id)
    if not empresa:
        return json.dumps(
            {"erro": f"Empresa '{empresa_id}' não encontrada. Use listar_empresas() para ver os IDs disponíveis."},
            ensure_ascii=False,
        )

    nome_empresa = empresa["nome"]
    historico = empresa["historico_mensal"]
    contatos = empresa["contatos"]

    valores = [float(m["valor_total"]) for m in historico]

    # Conjuntos históricos globais da empresa (todos os meses)
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
        valor = float(mes["valor_total"])

        # --- Validação de valor (leave-one-out) ---
        outros = [v for j, v in enumerate(valores) if j != i]
        media = sum(outros) / len(outros) if outros else 0.0
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

        # Conjuntos dos OUTROS meses para comparação
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
                "mes": mes["mes"],
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
    contemplando divergências de valor, localização ausente, fornecedor novo e/ou item novo.

    Args:
        nome_aprovador (str): Nome completo do aprovador a ser acionado.
        empresa_nome (str): Nome da empresa à qual a compra pertence.
        pedido_id (str): Mês de referência ou ID do pedido com divergência.
        item (str): Período ou item com incoerência.
        fornecedor (str): Nome do(s) fornecedor(es) da compra.
        valor_atual (float): Valor atual da compra (total mensal ou unitário).
        media_historica (float): Média histórica de referência (0 se não aplicável).
        variacao_percentual (float): Percentual de variação acima da média (0 se N/A).
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
        pedido_id (str): Mês de referência ou ID do pedido.
        aprovador_1_nome (str): Nome completo do primeiro aprovador.
        aprovador_1_cargo (str): Cargo/Área do primeiro aprovador.
        aprovador_1_status (str): "Confirmado", "Rejeitado" ou "Pendente".
        aprovador_2_nome (str): Nome completo do segundo aprovador.
        aprovador_2_cargo (str): Cargo/Área do segundo aprovador.
        aprovador_2_status (str): "Confirmado", "Rejeitado" ou "Pendente".
        tipos_divergencia_json (str): JSON com flags dos tipos de divergência.
            Exemplo: {"valor_atipico": true, "localizacao_ausente": false}

    Returns:
        str: Relatório final formatado com empresa, status, tipos de divergência
             e contatos acionados nominalmente.
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
    if tipos.get("valor_atipico") or tipos.get("preco_incoerente"):
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
