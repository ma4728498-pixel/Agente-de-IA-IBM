# Roteiro do Vídeo — Agente de Conformidade de Compras VF
## IBM SkillsBuild AI Experiential Learning Lab for Brazil
### Duração: ~1:30

---

## [00:00 – 00:18] PROBLEMA — Dor concreta do stakeholder

**Falar (narração em voz):**

> "Ana Paula é Analista de Conformidade de Compras. Todo mês ela passa cerca de **5 horas** revisando manualmente as transações de 8 empresas do grupo — comparando valores, verificando fornecedores e localizações em planilhas separadas.
>
> Quando encontra uma irregularidade, leva mais **2 a 3 dias úteis** para escalar ao aprovador certo — e nesse intervalo o pagamento pode já ter sido processado."

**Mostrar na tela:** Slide simples com:
- Foto de ícone de analista + empresa
- "5 horas/mês revisando 8 empresas manualmente"
- "2–3 dias para acionar aprovadores"
- "Risco: pagamento processado antes da revisão"

---

## [00:18 – 00:35] SOLUÇÃO — IBM Bob no Agent Mode

**Falar:**

> "Com o Agente de Conformidade de Compras, Ana Paula entrega a nota fiscal diretamente ao **IBM Bob no Agent Mode** — e recebe o diagnóstico completo em segundos."

**Mostrar na tela:** Abrir o **IBM Bob** em Agent Mode.

Digitar no chat:

```
Processe a nota fiscal mcp/dados/nota_fiscal_INV-2026-1142.pdf
```

**Aguardar a resposta do Bob** — ele vai:
1. Acionar `processar_pdf_invoice` via MCP
2. Extrair campos do PDF (empresa, período, localização, line items)
3. Verificar conformidade de cada item em paralelo
4. Registrar no ERP
5. Retornar o diagnóstico completo

**Mostrar na tela:** A resposta do Bob com os line items verificados e as divergências detectadas.

---

## [00:35 – 00:55] DEMONSTRAÇÃO — Resultado e acionamento de aprovadores

**Falar:**

> "O Bob identificou que o item de **Consultoria de TI** tem um fornecedor novo — **TechParts Ltda** — que não consta no histórico da empresa. E o valor total está **23% acima da média histórica**.
>
> Os dois aprovadores responsáveis já foram acionados automaticamente."

**Mostrar na tela:** Detalhe da resposta do Bob com:
- Line items verificados (✅ em conformidade / ❌ divergência)
- Divergências identificadas
- E-mails de aprovação gerados para os 2 contatos

---

## [00:55 – 01:15] IMPACTO — Números concretos

**Falar:**

> "O que antes levava 5 horas e 2 dias agora leva menos de **10 segundos** — uma redução de **98% no tempo de trabalho** de Ana Paula. E 100% das transações são verificadas, sem nenhum item passar despercebido.
>
> O sistema escala: 100 empresas levam o mesmo tempo que 8."

**Mostrar na tela:** Tabela de impacto:

| Métrica | Antes | Depois |
|---|---|---|
| Auditoria mensal (8 empresas) | ~5 horas | ~5 minutos |
| Processar 1 nota fiscal | 20–30 min | < 10 segundos |
| Acionar aprovadores | 2–3 dias | Imediato |
| Redução de tempo (Ana Paula) | — | **~98%** |

---

## [01:15 – 01:30] TECNOLOGIA — Bob + MCP + paralelismo

**Falar:**

> "A solução usa o **IBM Bob no Agent Mode** como motor conversacional, com um servidor MCP que expõe 8 ferramentas especializadas — incluindo ingestão de PDF via pdfplumber, verificações paralelas por line item com ThreadPoolExecutor e gravação de resultado no ERP.
>
> O IBM Bob foi também o copiloto de engenharia que construiu toda a solução — do código ao diagrama de arquitetura."

**Mostrar na tela:** Diagrama de arquitetura (do README) com destaque no bloco IBM Bob.

---

## CHECKLIST ANTES DE GRAVAR

- [ ] IBM Bob aberto em **Agent Mode** (não em modo Ask ou Plan)
- [ ] MCP server rodando (verificar `.bob/mcp.json` carregado)
- [ ] Arquivo `mcp/dados/nota_fiscal_INV-2026-1142.pdf` acessível
- [ ] Testar o comando antes de gravar — confirmar que Bob chama `processar_pdf_invoice`
- [ ] Narração clara: mencionar "Agent Mode", "document ingestion", "nota fiscal PDF", "stakeholder Ana Paula", "5 horas", "98%"
- [ ] Duração total: 1:30 (máximo permitido)
