# Agente Analista de Conformidade de Compras — COM RAG

Agente nativo do IBM watsonx Orchestrate que audita o histórico mensal de compras
de 8 empresas corporativas (Mai–Out/2026), com dados armazenados em knowledge base (RAG).

## Estrutura

```
agente_com_rag/
├── analista_conformidade.yaml          # Spec do agente nativo
├── tools/
│   └── compras_tools.py                # 4 ferramentas Python
└── knowledge_base/
    ├── compras_kb.yaml                 # Spec da knowledge base
    └── docs/
        ├── empresas_corporativas.json  # Histórico + contatos das 8 empresas
        ├── historico_compras.csv       # Registros unitários com médias históricas
        └── matriz_aprovadores.json     # Contatos aprovadores (legado)
```

## Ferramentas

| Tool | Descrição |
|---|---|
| `auditar_historico_mensal_empresa` | Audita histórico mensal recebendo JSON da empresa via RAG |
| `auditar_compras` | Audita registros unitários com média histórica via RAG |
| `gerar_notificacao_aprovador` | Gera notificação formal para cada aprovador |
| `registrar_status_aprovacao` | Consolida relatório final por empresa/mês |

## Deploy

```bash
# 1. Ativar ambiente
orchestrate env activate <seu-ambiente>

# 2. Importar a knowledge base
orchestrate knowledge-bases import -f knowledge_base/compras_kb.yaml

# 3. Importar as ferramentas
orchestrate tools import -k python -f tools/compras_tools.py

# 4. Importar o agente
orchestrate agents import -f analista_conformidade.yaml
```
