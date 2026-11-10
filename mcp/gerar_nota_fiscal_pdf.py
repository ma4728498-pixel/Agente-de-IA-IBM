"""
Gera o PDF de nota fiscal de exemplo para demonstração.
Execute: python mcp/gerar_nota_fiscal_pdf.py
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from pathlib import Path

OUTPUT = Path(__file__).parent / "dados" / "nota_fiscal_INV-2026-1142.pdf"

def gerar():
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    w, h = A4

    # Cabeçalho
    c.setFillColorRGB(0.06, 0.38, 0.99)  # IBM Blue
    c.rect(0, h - 3*cm, w, 3*cm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, h - 1.5*cm, "NOTA FISCAL DE SERVIÇOS / COMPRAS")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, h - 2.2*cm, "Beta Logística e Transportes Ltda  |  CNPJ: 12.345.678/0001-99")

    # Corpo
    c.setFillColorRGB(0, 0, 0)
    y = h - 4.5*cm

    def linha(label, valor, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        c.drawString(2*cm, y, f"{label}:")
        c.setFont("Helvetica", 10)
        c.drawString(7*cm, y, valor)
        y -= 0.65*cm

    linha("Número",          "INV-2026-1142", bold=True)
    linha("Data de Emissão", "05/11/2026")
    linha("Período",         "Novembro/2026")
    linha("Empresa ID",      "EMP-002")
    linha("Localização",     "Campinas, SP")

    y -= 0.4*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "ITENS DA NOTA FISCAL")
    y -= 0.3*cm
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.rect(2*cm, y - 0.5*cm, w - 4*cm, 0.6*cm, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2.2*cm, y - 0.2*cm, "Item")
    c.drawString(4*cm,   y - 0.2*cm, "Descrição")
    c.drawString(11*cm,  y - 0.2*cm, "Fornecedor")
    c.drawString(16.5*cm,y - 0.2*cm, "Valor (R$)")
    y -= 0.8*cm

    items = [
        ("LI-001", "Óleo Diesel S10 — 8.000 litros",         "Auto Posto Rodovia",    "12.800,00"),
        ("LI-002", "Arla 32 — 500 litros",                   "Auto Posto Rodovia",    " 1.200,00"),
        ("LI-003", "Pneus Radiais 295/80 R22.5 — 8 un.",     "Fornecedor NovoBrasil", "11.800,00"),
    ]

    c.setFont("Helvetica", 9)
    for i, (item_id, desc, forn, val) in enumerate(items):
        if i % 2 == 0:
            c.setFillColorRGB(0.98, 0.98, 0.98)
            c.rect(2*cm, y - 0.45*cm, w - 4*cm, 0.6*cm, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(2.2*cm, y - 0.15*cm, item_id)
        c.drawString(4*cm,   y - 0.15*cm, desc)
        c.drawString(11*cm,  y - 0.15*cm, forn)
        c.drawString(16.5*cm,y - 0.15*cm, val)
        y -= 0.65*cm

    # Total
    y -= 0.3*cm
    c.setFillColorRGB(0.06, 0.38, 0.99)
    c.rect(2*cm, y - 0.5*cm, w - 4*cm, 0.65*cm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.2*cm,  y - 0.15*cm, "VALOR TOTAL")
    c.drawString(16.5*cm, y - 0.15*cm, "25.800,00")

    # Rodapé
    c.setFillColorRGB(0.44, 0.44, 0.44)
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, 1.5*cm, "Documento gerado pelo Agente de Conformidade de Compras VF · IBM Bob · IBM watsonx Orchestrate")

    c.save()
    print(f"PDF gerado: {OUTPUT}")

if __name__ == "__main__":
    gerar()
