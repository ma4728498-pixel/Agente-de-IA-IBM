# Agente de IA: Analista de Conformidade de Compras 🤖📋

Agente inteligente desenvolvido para o **IBM watsonx Orchestrate** especializado em **auditoria de compras e controle de conformidade com fluxo de dupla aprovação**.

---

## 📌 Visão Geral

O agente `analista_conformidade_compras` monitora o histórico de compras, identifica inconformidades operacionais/financeiras e aciona automaticamente os aprovadores formais da empresa (ex.: Gerente de Compras e Diretor Financeiro), consolidando o status de aprovação.

### 🔍 Critérios de Incoerência Auditados
1. **Preço Atípico:** Transações com valor unitário **> 15% acima da média histórica** do item.
2. **Localização Ausente:** Pedidos em que o campo de localização de origem da compra está vazio, em branco ou nulo.
3. **Discrepância Documental:** Divergências entre o valor da Ordem de Compra e da Nota Fiscal.

---

## 📁 Estrutura do Projeto

```text
├── agents/
│   └── analista_conformidade.yaml        # Especificação do agente no watsonx Orchestrate
├── knowledge_base/
│   ├── compras_kb.yaml                   # Configuração e especificação da base de conhecimento
│   └── docs/
│       ├── historico_compras.csv         # Dados históricos de pedidos e médias de referência
│       └── matriz_aprovadores.csv        # Cadastro dos contatos e aprovadores autorizados
├── tools/
│   └── compras_tools.py                  # Ferramentas Python (@tool) para auditoria e notificações
├── .gitignore                            # Arquivos e diretórios ignorados pelo Git
└── README.md                             # Documentação do projeto
```

> **Nota sobre a Knowledge Base:** O IBM watsonx Orchestrate suporta arquivos textuais como `.csv`, `.txt`, `.docx`, `.pdf`, etc. Arquivos no formato `.json` direto não são aceitos pelo indexador de documentos da Knowledge Base, razão pela qual a matriz de aprovadores é mantida em `.csv`.

---

## 🚀 Guia Detalhado de Instalação e Deploy

Este guia detalha o processo completo de configuração, resolução de problemas comuns e implantação do agente no **IBM watsonx Orchestrate**.

---

### Etapa 1: Preparação do Ambiente e Dependências

#### 1.1. Pré-requisitos de Sistema
- **Python**: Versão **3.11** ou superior (compatível até 3.14).
  ```bash
  python --version
  ```
- Acesso com perfil administrativo ou de desenvolvedor a uma instância do **IBM watsonx Orchestrate**.

#### 1.2. Instalação do Toolkit CLI Oficial
Abra seu terminal (Prompt de Comando ou PowerShell) e execute a instalação do pacote do Agent Development Kit (ADK):
```bash
pip install --upgrade ibm-watsonx-orchestrate
```

#### 1.3. Ajuste da Variável de Ambiente `PATH` (Windows)
Em instalações do Python pelo Windows (especialmente via Microsoft Store), o diretório de scripts e executáveis não vem adicionado ao `PATH` do sistema por padrão, gerando o erro:
> `'orchestrate' não é reconhecido como um comando interno ou externo...`

Para resolver definitivamente:
1. Abra o **PowerShell** e execute o comando abaixo para registrar a pasta no seu `PATH` de usuário:
   ```powershell
   $scriptsPath = "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts"
   $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
   if ($currentPath -notlike "*$scriptsPath*") {
       [Environment]::SetEnvironmentVariable("Path", "$currentPath;$scriptsPath", "User")
       Write-Host "PATH atualizado com sucesso!"
   }
   ```
2. Feche e reabra o terminal para recarregar as variáveis de ambiente.
3. Teste se o comando está respondendo:
   ```bash
   orchestrate --help
   ```

---

### Etapa 2: Obtenção das Credenciais da Instância IBM

Para conectar a CLI à sua instância na nuvem, você precisa da **Service Instance URL** e da **WXO API Key**.

> ⚠️ **Atenção Importante sobre URLs:**
> **NUNCA** utilize o endereço do navegador (ex: `https://eu-de.watson-orchestrate.cloud.ibm.com/`). Usar a URL do frontend fará o servidor devolver uma página HTML de login, gerando o erro:
> `requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1`
> É obrigatório utilizar a URL da API da sua instância fornecida na página de configurações.

#### Como localizar no painel web:
1. Faça login na sua conta do **IBM watsonx Orchestrate**.
2. Clique no seu **ícone de perfil/usuário** no canto superior direito.
3. Clique em **Settings (Configurações)**.
4. Navegue até a aba **API details (Detalhes da API)**.
5. Localize e copie os campos:
   - **Service instance URL:** Algo no padrão:
     `https://api.<regiao>.watson-orchestrate.ibm.com/instances/<instance_id>`
   - **API Key (WXO API Key):** Caso não tenha uma gerada, clique em **Generate API key** (ou use sua chave IAM gerada em *Manage > Access (IAM) > API Keys* no IBM Cloud).

---

### Etapa 3: Configurar e Ativar o Ambiente na CLI

Com a URL e a chave em mãos, registre o ambiente no terminal:

#### 3.1. Adicionar o ambiente:
```bash
orchestrate env add -n meu-ambiente -u "https://api.<regiao>.watson-orchestrate.ibm.com/instances/<SEU_INSTANCE_ID>"
```
*(Caso queira substituir um ambiente configurado incorretamente, use antes: `orchestrate env remove -n meu-ambiente`)*.

#### 3.2. Ativar o ambiente:
```bash
orchestrate env activate meu-ambiente
```
O terminal solicitará a sua chave:
```text
Please enter WXO API key:
```
- Cole a chave copiada (o terminal pode não exibir os caracteres por segurança) e pressione **Enter**.
- Para verificar se o ambiente está ativo e selecionado:
  ```bash
  orchestrate env list
  ```
  *(O ambiente ativo será marcado com um asterisco ou status `active`)*.

---

### Etapa 4: Requisitos e Cuidados com os Arquivos do Projeto

Antes de disparar os comandos de importação, certifique-se de que os arquivos respeitem as regras do watsonx Orchestrate:

1. **Formatos da Knowledge Base:**
   - O indexador do watsonx Orchestrate aceita: `.csv`, `.txt`, `.docx`, `.pdf`, `.pptx`, `.xlsx`, `.html`.
   - **Não utilize arquivos `.json` diretamente na lista de documentos** (geraria o erro `Unsupported file type application/json`). Por isso, cadastros como `matriz_aprovadores` devem estar em formato `.csv`.
2. **Caminhos Relativos no YAML:**
   - No arquivo `knowledge_base/compras_kb.yaml`, os caminhos na seção `documents:` devem ser relativos à pasta onde o próprio YAML reside (ou seja, `docs/historico_compras.csv` e `docs/matriz_aprovadores.csv`), e **não** `knowledge_base/docs/...`.

---

### Etapa 5: Executar o Deploy dos Recursos (Ordem Estrita)

Navegue até a pasta raiz do projeto (`Orca`) no seu terminal e execute os comandos rigorosamente na seguinte ordem de dependência:

#### Passo 5.1: Importar a Base de Conhecimento (Knowledge Base)
Cria o repositório vetorial e indexa os documentos de compras e aprovadores:
```bash
orchestrate knowledge-bases import -f knowledge_base/compras_kb.yaml
```
*(Ao concluir, a base `compras_conformidade_kb` estará pronta para receber consultas semânticas do agente).*

#### Passo 5.2: Importar as Ferramentas Python (Python Tools)
Registra as funções decoradas com `@tool` do módulo `compras_tools.py` no catálogo de ferramentas do ambiente:
```bash
orchestrate tools import -k python -f tools/compras_tools.py
```
*(As ferramentas `auditar_compras`, `gerar_notificacao_aprovador` e `registrar_status_aprovacao` ficarão disponíveis para os agentes).*

#### Passo 5.3: Importar e Vincular o Agente
Compila a especificação declarativa, conectando o LLM às ferramentas registradas e à base de conhecimento:
```bash
orchestrate agents import -f agents/analista_conformidade.yaml
```
*(O agente `analista_conformidade_compras` é publicado na sua instância e fica disponível para uso imediato).*

#### Passo 5.4: Validação do Deploy via CLI (Opcional)
Você pode listar os recursos no terminal para confirmar a implantação:
```bash
orchestrate knowledge-bases list
orchestrate tools list
orchestrate agents list
```

---

## 💬 Como Usar e Testar o Agente

Após concluir a importação, acesse a interface web do **IBM watsonx Orchestrate**, abra o chat com o agente **`analista_conformidade_compras`** e teste os fluxos abaixo:

### 1. Auditoria Geral de Pedidos
> *"Analise o histórico de compras, identifique quais transações possuem divergências ou dados faltantes e acione os aprovadores responsáveis."*

**Comportamento esperado:**
- Consulta a base de conhecimento e identifica transações incoerentes (ex.: `PED-003`, `PED-005` por preço alto; `PED-006`, `PED-007` por localização ausente).
- Gera 2 notificações formais por transação direcionadas à Gerente de Compras (Ana Paula) e ao Diretor Financeiro (Carlos Eduardo).
- Registra o status consolidado como `Pendente de Confirmação`.

### 2. Simulação de Resposta dos Aprovadores (Dupla Aprovação)
> *"Para o pedido PED-006, tanto Ana Paula Ferreira quanto Carlos Eduardo Lima responderam 'APROVADO'. Atualize o status da operação."*

**Comportamento esperado:**
- O agente chama `registrar_status_aprovacao` e atualiza o status final para **`Aprovado`**.

### 3. Simulação de Rejeição
> *"Para o pedido PED-003, o Diretor Financeiro Carlos Eduardo Lima respondeu 'REJEITADO'. Qual o status final da compra?"*

**Comportamento esperado:**
- Como um dos aprovadores rejeitou, o status da operação é consolidado como **`Rejeitado`**.
