# Exemplos de Saída — agente_conformidade_VF

Saídas reais geradas pela execução direta das ferramentas do agente com dados da
knowledge base (`empresas_corporativas.json`).

---

## Cenário A — Fornecedor novo (1 critério)

**Empresa:** Eta Energia Solar e Sustentabilidade (EMP-007)  
**Mês analisado:** Outubro/2026  
**Valor total:** R$ 52.400,00 | **Média histórica:** R$ 48.940,00 | **Variação:** +7,07%

**Critérios verificados:**
- ❌ Valor > 15%: NÃO (+7,07% — abaixo do limiar)
- ✅ Fornecedor novo: SIM — *Phoenix Contact* nunca apareceu nos meses anteriores
- ❌ Localização nova: NÃO — *Brasília, DF* está no histórico

### Saída de `verificar_conformidade_transacao`

```json
{
  "requer_aprovacao": true,
  "empresa_nome": "Eta Energia Solar e Sustentabilidade",
  "empresa_id": "EMP-007",
  "pedido_id": "Outubro/2026",
  "valor_total_atual": 52400.0,
  "media_historica_mensal": 48940.0,
  "variacao_percentual": 7.07,
  "fornecedores_novos": ["Phoenix Contact"],
  "localizacao_atual": "Brasília, DF",
  "localizacao_nova": false,
  "divergencias": [
    "Fornecedor(es) não encontrado(s) no histórico de compras: Phoenix Contact"
  ],
  "tipos_divergencia": {
    "valor_atipico": false,
    "fornecedor_novo": true,
    "localizacao_nova_ou_ausente": false
  }
}
```

### Bloco de resposta final do agente

```
STATUS DE CONFORMIDADE: Requer Aprovação
EMPRESA: Eta Energia Solar e Sustentabilidade
PEDIDO/REFERÊNCIA: Outubro/2026

CRITÉRIOS VERIFICADOS:
  • Valor total > 15% acima da média: NÃO (+7.07%)
  • Fornecedor novo (não encontrado no histórico): SIM → Phoenix Contact
  • Localização nova (não encontrada no histórico): NÃO

CONTATOS ACIONADOS PARA APROVAÇÃO:
- Contato 1: Tatiana Farias (Tesouraria)
  E-mail: tatiana.farias@etasolar.com | Tel: (61) 98444-1212
  Status: Pendente de Resposta
- Contato 2: Marcelo H. Diniz (Gerente de Projetos de Engenharia)
  E-mail: marcelo.diniz@etasolar.com | Tel: (61) 98444-3434
  Status: Pendente de Resposta
```

---

## Cenário B — Todos os 3 critérios disparados

**Empresa:** Eta Energia Solar e Sustentabilidade (EMP-007)  
**Mês analisado:** Outubro/2026 (versão simulada com localização e valor alterados)  
**Valor total:** R$ 57.000,00 | **Média histórica:** R$ 48.940,00 | **Variação:** +16,47%

**Critérios verificados:**
- ✅ Valor > 15%: SIM (+16,47%)
- ✅ Fornecedor novo: SIM — *Phoenix Contact*
- ✅ Localização nova: SIM — *Goiânia, GO* (histórico só tem *Brasília, DF*)

### Saída de `enviar_solicitacao_aprovacao_conformidade`

```
SOLICITAÇÃO DE APROVAÇÃO ENVIADA
═══════════════════════════════════════════════════════════════
EMPRESA        : Eta Energia Solar e Sustentabilidade
PEDIDO/REF.    : Outubro/2026
VALOR ATUAL    : R$ 57,000.00
MÉDIA HISTÓRICA: R$ 48,940.00
VARIAÇÃO       : 16.5%
LOCALIZAÇÃO    : Goiânia, GO

DIVERGÊNCIAS QUE MOTIVARAM O ENVIO:
  • Valor total R$57,000.00 está 16.5% acima da média histórica R$48,940.00 (limite: 15%)
  • Fornecedor(es) não encontrado(s) no histórico de compras: Phoenix Contact
  • Localização 'Goiânia, GO' não se encontra no histórico de compras desta empresa

CONTATOS ACIONADOS:
- Contato 1: Tatiana Farias (Tesouraria)
  E-mail: tatiana.farias@etasolar.com | Tel: (61) 98444-1212
  Status: Pendente de Resposta

- Contato 2: Marcelo H. Diniz (Gerente de Projetos de Engenharia)
  E-mail: marcelo.diniz@etasolar.com | Tel: (61) 98444-3434
  Status: Pendente de Resposta

─────────────────────────────────────────────────────────────────────
MODELOS DE E-MAIL GERADOS PARA ENVIO
─────────────────────────────────────────────────────────────────────

─────────────────────────────────────────────────────────────────
  SOLICITAÇÃO DE APROVAÇÃO — TATIANA FARIAS
  Para: tatiana.farias@etasolar.com
  Assunto: [CONFORMIDADE — APROVAÇÃO NECESSÁRIA] Divergência detectada — Eta Energia Solar e Sustentabilidade / Outubro/2026
─────────────────────────────────────────────────────────────────

  Prezado(a) Tatiana Farias,

  O sistema de Conformidade de Compras identificou divergências na
  transação abaixo que requerem sua aprovação formal:

    • Empresa    : Eta Energia Solar e Sustentabilidade
    • Referência : Outubro/2026
    • Valor      : R$ 57,000.00 (+16.5% acima da média R$ 48,940.00)
    • Localização: Goiânia, GO
  Fornecedor(es) NÃO encontrado(s) no histórico:
    ⚠️ Phoenix Contact

  Divergências identificadas:
    - Valor total R$57,000.00 está 16.5% acima da média histórica R$48,940.00 (limite: 15%)
    - Fornecedor(es) não encontrado(s) no histórico de compras: Phoenix Contact
    - Localização 'Goiânia, GO' não se encontra no histórico de compras desta empresa

  Por favor, responda a este e-mail com:
    ✅ APROVADO — informe a justificativa para prosseguir.
    ❌ REJEITADO — a ordem de compra será cancelada automaticamente.

  Prazo para resposta: 48 horas a partir do recebimento deste e-mail.

  Atenciosamente,
  Sistema de Conformidade de Compras — Agente de Conformidade VF
─────────────────────────────────────────────────────────────────

─────────────────────────────────────────────────────────────────
  SOLICITAÇÃO DE APROVAÇÃO — MARCELO H. DINIZ
  Para: marcelo.diniz@etasolar.com
  Assunto: [CONFORMIDADE — APROVAÇÃO NECESSÁRIA] Divergência detectada — Eta Energia Solar e Sustentabilidade / Outubro/2026
─────────────────────────────────────────────────────────────────

  Prezado(a) Marcelo H. Diniz,

  O sistema de Conformidade de Compras identificou divergências na
  transação abaixo que requerem sua aprovação formal:

    • Empresa    : Eta Energia Solar e Sustentabilidade
    • Referência : Outubro/2026
    • Valor      : R$ 57,000.00 (+16.5% acima da média R$ 48,940.00)
    • Localização: Goiânia, GO
  Fornecedor(es) NÃO encontrado(s) no histórico:
    ⚠️ Phoenix Contact

  Divergências identificadas:
    - Valor total R$57,000.00 está 16.5% acima da média histórica R$48,940.00 (limite: 15%)
    - Fornecedor(es) não encontrado(s) no histórico de compras: Phoenix Contact
    - Localização 'Goiânia, GO' não se encontra no histórico de compras desta empresa

  Por favor, responda a este e-mail com:
    ✅ APROVADO — informe a justificativa para prosseguir.
    ❌ REJEITADO — a ordem de compra será cancelada automaticamente.

  Prazo para resposta: 48 horas a partir do recebimento deste e-mail.

  Atenciosamente,
  Sistema de Conformidade de Compras — Agente de Conformidade VF
─────────────────────────────────────────────────────────────────
```

---

## Cenário C — Transação em conformidade (sem aprovação)

**Empresa:** Alpha Tech Soluções S.A. (EMP-001)  
**Mês analisado:** Outubro/2026  
**Valor total:** R$ 4.530,00 | **Média histórica:** ~R$ 4.698,00 | **Variação:** -3,57%

**Critérios verificados:**
- ❌ Valor > 15%: NÃO (valor abaixo da média)
- ❌ Fornecedor novo: NÃO — *Fast Shop* foi fornecedor anteriormente / principais são históricos
- ❌ Localização nova: NÃO — *São Paulo, SP* está no histórico

### Bloco de resposta final do agente

```
STATUS DE CONFORMIDADE: Em Conformidade
EMPRESA: Alpha Tech Soluções S.A.
PEDIDO/REFERÊNCIA: Outubro/2026

CRITÉRIOS VERIFICADOS:
  • Valor total > 15% acima da média: NÃO (-3.57%)
  • Fornecedor novo (não encontrado no histórico): NÃO
  • Localização nova (não encontrada no histórico): NÃO

Nenhuma divergência detectada. A transação está em conformidade e
não requer aprovação adicional.
```

---

## Cenário D — Fluxo completo: ingestão de nota fiscal PDF com extração paralela de line items

> **Este é o caso de uso central do IBM Bob no Agent Mode.**  
> O usuário entrega ao Bob a nota fiscal em PDF com uma instrução em linguagem natural.  
> O Bob aciona `processar_pdf_invoice` via MCP, que extrai o documento com `pdfplumber`,  
> processa cada line item em paralelo (`ThreadPoolExecutor`, 3 workers simultâneos) e  
> registra o resultado no mock ERP — tudo em uma única interação conversacional.

**Arquivo:** `nota_fiscal_INV-2026-1142.pdf`  
**Trigger:** Usuário digita *"Processe a nota fiscal INV-2026-1142.pdf"* no IBM Bob (Agent Mode)  
**Empresa:** Beta Logística e Transportes Ltda (EMP-002)  
**Período:** Novembro/2026 | **Localização:** Campinas, SP | **Valor total:** R$ 25.800,00

### Instrução ao Bob

```
Processe a nota fiscal mcp/dados/nota_fiscal_INV-2026-1142.pdf
```

### Saída real de `processar_pdf_invoice`

```json
{
  "invoice_id": "INV-2026-1142",
  "fonte": "PDF",
  "arquivo": "nota_fiscal_INV-2026-1142.pdf",
  "empresa_id": "EMP-002",
  "periodo_referencia": "Novembro/2026",
  "localizacao": "Campinas, SP",
  "valor_total": 25800.0,
  "resumo": {
    "total_line_items": 3,
    "workers_paralelos": 3,
    "requer_aprovacao": true,
    "divergencias": [
      "Valor total R$25,800.00 está 101.7% acima da média histórica R$12,791.67 (limite: 15%)",
      "Fornecedor(es) não encontrado(s) no histórico: Fornecedor NovoBrasil"
    ],
    "erp_atualizado": true
  },
  "line_items_processados": [
    {
      "item_id": "LI-001",
      "descricao": "Óleo Diesel S10 — 8.000 litros",
      "fornecedor": "Auto Posto Rodovia",
      "valor": 12800.0,
      "fornecedor_aprovado": true,
      "divergencias_item": []
    },
    {
      "item_id": "LI-002",
      "descricao": "Arla 32 — 500 litros",
      "fornecedor": "Auto Posto Rodovia",
      "valor": 1200.0,
      "fornecedor_aprovado": true,
      "divergencias_item": []
    },
    {
      "item_id": "LI-003",
      "descricao": "Pneus Radiais 295/80 R22.5 — 8 unidades",
      "fornecedor": "Fornecedor NovoBrasil",
      "valor": 11800.0,
      "fornecedor_aprovado": false,
      "divergencias_item": [
        "Fornecedor(es) não encontrado(s) no histórico: Fornecedor NovoBrasil"
      ]
    }
  ],
  "contatos_aprovadores": [
    {
      "tipo": "Administrativo",
      "nome": "Marcos Vinícius",
      "area": "Gestão de Frota",
      "email": "marcos.vinicius@betalogistica.com",
      "telefone": "(11) 97654-1111"
    },
    {
      "tipo": "Pessoa de Confiança",
      "nome": "Juliano Antunes",
      "area": "Gerente de Operações",
      "email": "juliano.antunes@betalogistica.com",
      "telefone": "(11) 97654-2222"
    }
  ]
}
```

### O que aconteceu internamente

| Etapa | Descrição |
|---|---|
| **1. Trigger** | Bob recebe instrução em linguagem natural no Agent Mode |
| **2. PDF Ingestion** | `processar_pdf_invoice` extrai cabeçalho e tabela de line items via `pdfplumber` |
| **3. Extração paralela** | `ThreadPoolExecutor` despacha 3 workers simultâneos — um por line item |
| **4. Verificação por item** | Cada worker verifica fornecedor do item contra o histórico da KB |
| **5. Verificação consolidada** | Valor total e localização verificados contra a média histórica da EMP-002 |
| **6. Registro no ERP** | Resultado estruturado gravado em `erp_mock.json` com status e divergências |
| **7. Resposta ao Bob** | JSON estruturado devolvido; Bob consolida e apresenta diagnóstico ao usuário |

### Resultado

- ✅ LI-001 (Óleo Diesel — Auto Posto Rodovia): **Em conformidade**
- ✅ LI-002 (Arla 32 — Auto Posto Rodovia): **Em conformidade**
- ❌ LI-003 (Pneus — Fornecedor NovoBrasil): **Fornecedor não homologado**
- ❌ Valor total R$ 25.800,00: **101,7% acima da média histórica** (R$ 12.791,67)

**Aprovadores acionados:** Marcos Vinícius e Juliano Antunes (Beta Logística e Transportes Ltda)
