# Agente Analista de Conformidade de Compras — SEM RAG

Agente nativo do IBM watsonx Orchestrate que audita o histórico mensal de compras
de 8 empresas corporativas (Mai–Out/2026). **Todos os dados estão embutidos
diretamente nas ferramentas Python** — sem dependência de knowledge base ou RAG.

## Estrutura

```
agente_sem_rag/
├── analista_conformidade_sem_rag.yaml  # Spec do agente nativo
└── tools/
    └── compras_tools_sem_rag.py        # 4 ferramentas Python (dados embutidos)
```

## Ferramentas

| Tool | Descrição |
|---|---|
| `listar_empresas` | Retorna ID + nome das 8 empresas disponíveis |
| `auditar_empresa` | Audita empresa pelo ID — dados e contatos embutidos na tool |
| `gerar_notificacao_aprovador` | Gera notificação formal para cada aprovador |
| `registrar_status_aprovacao` | Consolida relatório final por empresa/mês |

## Deploy

```bash
# 1. Ativar ambiente
orchestrate env activate <seu-ambiente>

# 2. Importar as ferramentas (sem etapa de knowledge base)
orchestrate tools import -k python -f tools/compras_tools_sem_rag.py

# 3. Importar o agente
orchestrate agents import -f analista_conformidade_sem_rag.yaml
```
