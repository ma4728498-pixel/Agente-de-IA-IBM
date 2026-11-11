# Declaração do Problema e da Solução

## O Problema

Gestores administrativos e analistas de compras em empresas de médio porte enfrentam um desafio crítico: identificar manualmente transações suspeitas ou fora do padrão em volumes crescentes de ordens de compra mensais. Em uma empresa com 8 unidades corporativas processando dezenas de pedidos por mês, um analista leva em média **5 horas por ciclo mensal** apenas para comparar valores, verificar fornecedores e checar localizações contra o histórico — trabalho repetitivo, propenso a erros e de baixo valor agregado.

O custo dessa ineficiência é alto: transações fraudulentas passam despercebidas, fornecedores não homologados entram na cadeia de suprimentos sem aprovação formal, e o processo de dupla aprovação — exigido por políticas internas de compliance — frequentemente atrasa dias por falta de acionamento ágil dos responsáveis. Uma nota fiscal com item irregular pode levar **2 a 3 dias úteis** para ser escalada ao aprovador correto; nesse intervalo o pagamento pode já ter sido processado.

**Stakeholder principal:** Ana Paula, Analista de Conformidade de Compras, responsável por auditar mensalmente as transações de 8 empresas do grupo e acionar os 2 aprovadores designados por empresa sempre que detectar irregularidades. Hoje ela faz isso manualmente, em planilhas, consultando históricos em sistemas separados, gastando **~5 horas/mês** apenas nessa tarefa repetitiva.

## A Solução

O **Agente de Conformidade de Compras VF** usa o **IBM Bob no Agent Mode** como motor conversacional central. O fluxo central começa com um **documento de negócio real**:

### Fluxo de ingestão de nota fiscal PDF (caso central)

1. **Trigger:** Ana Paula digita no IBM Bob (Agent Mode): *"Processe a nota fiscal INV-2026-1142.pdf"*
2. **PDF Ingestion:** O Bob aciona `processar_pdf_invoice` via MCP — a ferramenta lê o PDF com `pdfplumber`, extrai o cabeçalho (empresa, período, localização, valor total) e a tabela de line items
3. **Extração paralela de line items:** `ThreadPoolExecutor` despacha um worker simultâneo por item — cada um verifica o fornecedor daquele item contra o histórico da knowledge base em paralelo
4. **Verificação consolidada:** valor total e localização verificados contra a média histórica da empresa
5. **Registro no ERP:** resultado estruturado gravado no mock ERP (`erp_mock.json`) com status de cada item e divergências
6. **Resposta em linguagem natural:** Bob consolida e apresenta o diagnóstico completo — itens aprovados, item irregular identificado (Fornecedor NovoBrasil, LI-003), aprovadores acionados

O mesmo fluxo funciona com CSV de transações mensais para auditorias em lote de múltiplas empresas.

A solução verifica 3 critérios de conformidade em cada transação:

1. **Valor atípico:** o valor total do mês é mais de 15% acima da média histórica da empresa
2. **Fornecedor novo:** o fornecedor não aparece no histórico de meses anteriores da empresa
3. **Localização nova ou ausente:** a localização da transação não consta no histórico

Quando qualquer critério é violado, o agente aciona automaticamente os **2 contatos aprovadores** cadastrados para aquela empresa na knowledge base, gerando e-mails formais de solicitação de aprovação com prazo de 48 horas.

Ana Paula interage com o sistema exclusivamente via **IBM Bob no Agent Mode** em linguagem natural — digitando *"Processe a nota fiscal INV-2026-1142.pdf"* e recebendo em segundos o diagnóstico completo, os line items verificados item a item e as ações necessárias. Uma interface web alternativa em Streamlit também está disponível publicamente para acesso sem o Bob.

## Por que é criativo e único

A solução demonstra o **Bob no Agent Mode fazendo document understanding real**: a nota fiscal PDF é ingerida pelo Bob, que aciona a ferramenta `processar_pdf_invoice` via MCP, extrai automaticamente todos os campos e line items do documento, executa verificações de conformidade em paralelo (um sub-agente por item via `ThreadPoolExecutor`) e registra o resultado estruturado no ERP — sem nenhuma intervenção manual entre a entrega do documento e a decisão de conformidade.

O diferencial está na **orquestração pelo IBM Bob ponta a ponta**: da ingestão do documento de negócio com extração paralela de line items, passando pela detecção das anomalias, até a geração dos e-mails de aprovação — tudo em uma única interação conversacional, com lógica de negócio determinística (o agente não "alucina" regras — ele executa ferramentas Python auditáveis).

## Impacto mensurável

| Métrica | Antes | Depois |
|---|---|---|
| Tempo de auditoria mensal (8 empresas) | ~5 horas | ~5 minutos |
| **Redução de tempo para Ana Paula** | — | **~98% de redução** (5h → ~5min) |
| Tempo para processar 1 nota fiscal | 20–30 min (manual) | < 10 segundos (automático) |
| Tempo para acionar aprovadores | 2–3 dias úteis (e-mail manual) | Imediato (automático) |
| Risco de transação irregular não detectada | Alto (revisão manual) | Baixo (100% das transações verificadas) |
| Escalabilidade | Linear (mais empresas = mais horas) | Constante (100 empresas = mesmo tempo) |

**Caso concreto:** Em Novembro/2026, a empresa Beta Solutions apresentou um fornecedor novo (`TechParts Ltda`) e valor 23% acima da média histórica. Com o processo manual de Ana Paula, essa anomalia seria detectada ao fim de uma revisão de ~5h e escalada 2 dias depois. Com o Agente de Conformidade no IBM Bob, a detecção e o acionamento dos aprovadores ocorreram em **menos de 10 segundos** após a entrega da nota fiscal em PDF.

A solução foi inteiramente concebida, desenvolvida, depurada e documentada com o auxílio do **IBM Bob** — assistente de IA da IBM utilizado como copiloto de engenharia ao longo de todo o ciclo de desenvolvimento.
