# Declaração da Tecnologia Utilizada

## IBM Bob — Copiloto de Engenharia Central

O **IBM Bob** foi utilizado como assistente de desenvolvimento ao longo de **todo o ciclo de vida do projeto** — da concepção à entrega. Abaixo estão os usos específicos e verificáveis:

### 1. Arquitetura e design do sistema
Bob analisou a estrutura inicial do projeto (dois projetos misturados no mesmo repositório, com `knowledge_base/` dentro de `knowledge_base/`) e propôs e executou a reorganização completa — movendo arquivos para as pastas corretas, eliminando duplicatas e criando uma estrutura limpa e deployável.

### 2. Desenvolvimento do frontend (app.py)
O arquivo `app.py` (interface Streamlit) foi integralmente criado pelo IBM Bob, incluindo:
- Conexão com o SDK do IBM watsonx Orchestrate via `execute_agent_interaction_with_fallback`
- Sistema de renderização enriquecida da resposta do agente (parser de markdown → HTML visual com cards de status, critérios com ✅/❌, cards de contatos lado a lado, expander de e-mails)
- Suporte dual a credenciais: `st.secrets` (Streamlit Cloud) e `.env` (local)
- Botões de ação rápida, sidebar com dados da knowledge base, exibição de reasoning trace

### 3. Depuração e resolução de problemas
Bob diagnosticou e corrigiu múltiplos problemas em tempo real:
- Identificou que o CLI `orchestrate` estava instalado em `AppData\Roaming` (não `AppData\Local`) e adicionou o caminho ao PATH do sistema
- Identificou que a URL da instância deveria ser `api.eu-de.watson-orchestrate.cloud.ibm.com` (não `api.eu-de.watson-orchestrate.ibm.com`) via DNS lookup
- Identificou que o agente retorna markdown com hífens não-quebrantes (`‑` U+2011) e corrigiu os regex de extração de contatos
- Corrigiu o bug de `**` literais aparecendo na interface ao perceber que o agente usa markdown onde o código esperava texto puro

### 4. Segurança e boas práticas
- Criou o `.gitignore` via git para proteger o `.env` do versionamento
- Criou o `.env.example` como template documentado
- Configurou o `requirements.txt` com versões fixas para deploy reproduzível

### 5. IBM Bob no Agent Mode — document ingestion de nota fiscal PDF como caso central

Este é o caso de uso central que demonstra o **Bob no Agent Mode fazendo document understanding de um business document real**.

**Fluxo completo (executado e documentado em `exemplo_saida.md`, Cenário D):**

| Etapa | Tecnologia | Descrição |
|---|---|---|
| **Trigger** | IBM Bob Agent Mode | Usuário digita: *"Processe a nota fiscal INV-2026-1142.pdf"* |
| **PDF Ingestion** | `pdfplumber` via MCP | Bob aciona `processar_pdf_invoice`; extrai cabeçalho + tabela de line items do PDF |
| **Extração paralela** | `ThreadPoolExecutor` | 3 workers simultâneos — um por line item — verificam fornecedores em paralelo na KB |
| **Verificação consolidada** | knowledge base (JSON) | Valor total e localização comparados contra média histórica da EMP-002 |
| **Registro ERP** | `erp_mock.json` | Resultado estruturado gravado com status por item e divergências detectadas |
| **Resposta ao usuário** | IBM Bob Agent Mode | Bob consolida JSON e apresenta diagnóstico em linguagem natural |

**Resultado real da execução com `nota_fiscal_INV-2026-1142.pdf` (EMP-002, Novembro/2026):**
- ✅ LI-001 — Óleo Diesel S10 (Auto Posto Rodovia): em conformidade
- ✅ LI-002 — Arla 32 (Auto Posto Rodovia): em conformidade
- ❌ LI-003 — Pneus Radiais (Fornecedor NovoBrasil): fornecedor não homologado
- ❌ Valor total R$ 25.800,00: 101,7% acima da média histórica (R$ 12.791,67)
- **Aprovadores acionados automaticamente:** Marcos Vinícius e Juliano Antunes

Bob projetou e implementou o servidor MCP em `mcp/server.py`, expondo 8 ferramentas ao IBM Bob via protocolo MCP (stdio). Cada ferramenta tem responsabilidade única e funciona como um **sub-agente especializado** orquestrado pelo Bob:

- `listar_empresas` — sub-agente de descoberta: retorna as 8 empresas da knowledge base
- `obter_empresa` — sub-agente de contexto: recupera histórico completo por ID ou nome
- `verificar_conformidade` — **sub-agente de auditoria**: aplica os 3 critérios de conformidade para uma empresa, buscando o histórico da KB internamente; retorna structured JSON output com `requer_aprovacao`, `divergencias`, `variacao_percentual` e `contatos_aprovadores`
- `enviar_solicitacao_aprovacao` — **sub-agente de notificação**: gera e-mails formais de aprovação para os 2 contatos responsáveis
- `analisar_lote_csv` — **document ingestion (CSV)**: ingere um arquivo CSV de transações e executa verificação para todas as empresas, retornando relatório consolidado
- `analisar_lote_csv_json` — **document ingestion + parallel sub-tasks + structured JSON output**: ingere o CSV e dispara verificações em paralelo via `ThreadPoolExecutor`, retornando JSON estruturado com `resumo`, `resultados` e `acoes_necessarias`
- `processar_invoice` — **document ingestion (JSON invoice)**: ingere invoice JSON, extrai line items em paralelo e grava no mock ERP
- `processar_pdf_invoice` — **document ingestion (PDF nota fiscal) — caso central do Agent Mode**: ingere PDF de nota fiscal via `pdfplumber`, extrai campos e line items, verifica conformidade de cada item em paralelo e registra no mock ERP

O servidor foi registrado em `.bob/mcp.json`. O IBM Bob atua como **orquestrador conversacional no Agent Mode**: recebe o caminho do documento de negócio em linguagem natural, aciona `processar_pdf_invoice` para document understanding, despacha sub-agentes de auditoria em paralelo e entrega o diagnóstico completo — tudo sem intervenção manual.

### 6. Documentação
Bob redigiu e atualizou o `README.md` com estrutura de projeto, instruções de deploy, diagrama de arquitetura Mermaid, seção de testes e instruções de registro do MCP server.

---

## IBM watsonx Orchestrate

O **IBM watsonx Orchestrate** (instância `eu-de`, região Europa) é o motor de orquestração da solução:

- **Agente nativo** `agente_conformidade_VF` configurado via YAML (`spec_version: v1`, `kind: native`, `style: react_core`) com fluxo obrigatório de 3 passos: (1) consultar KB, (2) chamar `verificar_conformidade_transacao`, (3) chamar `enviar_solicitacao_aprovacao_conformidade` se necessário
- **Knowledge Base RAG** `compras_conformidade_kb` alimentada por `empresas_corporativas.json` com histórico mensal de 8 empresas (Mai–Out/2026): valores totais, fornecedores, localizações e 2 contatos aprovadores por empresa; configurada com `retrieval_confidence_threshold: Low` e `query_rewrite: enabled`
- **2 ferramentas Python** registradas no IBM watsonx Orchestrate:
  - `verificar_conformidade_transacao`: aplica os 3 critérios de conformidade e retorna JSON com `requer_aprovacao`, `divergencias`, `tipos_divergencia` e `variacao_percentual`
  - `enviar_solicitacao_aprovacao_conformidade`: gera e-mails formais estruturados para os 2 aprovadores cadastrados na KB
- **SDK Python** `ibm-watsonx-orchestrate==2.19.1` usado no frontend Streamlit para comunicação via threads e runs com autenticação IAM gerada em runtime

## Modelo de linguagem

O agente utiliza o modelo configurado no IBM watsonx Orchestrate (`groq/openai/gpt-oss-120b`). Ele é responsável por interpretar as consultas em linguagem natural, orquestrar as chamadas às ferramentas na ordem correta e extrair os dados relevantes da knowledge base via RAG. Toda a lógica de negócio é delegada às ferramentas Python determinísticas — o modelo não inventa regras nem dados.

## IBM Bob

O **IBM Bob** é utilizado em duas dimensões:
- **Durante o desenvolvimento**: copiloto de engenharia que reorganizou o projeto, criou o frontend, diagnosticou bugs de configuração e gerou a documentação
- **Em produção**: motor conversacional central via servidor MCP — recebe linguagem natural, orquestra sub-agentes especializados, faz document ingestion de CSVs e entrega o fluxo completo de auditoria sem intervenção manual

## Ferramentas Open Source

| Ferramenta | Uso |
|---|---|
| **Python 3.14** | Implementação das tools, lógica de conformidade e servidor MCP |
| **Streamlit 1.67** | Interface web alternativa (acesso público via Streamlit Cloud) |
| **mcp[cli] 2.x** | Protocolo MCP (stdio) para integração direta com IBM Bob |
| **concurrent.futures** | ThreadPoolExecutor para verificações paralelas no lote CSV |
| **python-dotenv** | Gerenciamento de credenciais local |
| **Git** | Controle de versão |
