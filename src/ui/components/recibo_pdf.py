from fpdf import FPDF
import tempfile
import streamlit as st

def generar_recibo_pdf(usuario, monto, nro_recibo, periodo, deuda_anterior, consumo, reconexion):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="EPSA MUNICIPAL COLQUIRI", ln=1, align='C')
    pdf.cell(200, 10, txt="RECIBO DE PAGO", ln=1, align='C')
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Recibo N°: {nro_recibo}")
    pdf.cell(50, 10, txt=f"Fecha: {date.today()}")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Usuario: {usuario.codigo} - {usuario.nombre}")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Periodo: {periodo}")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Consumo: {consumo} m³")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Deuda anterior: {deuda_anterior} Bs")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Reconexión: {reconexion} Bs")
    pdf.ln(10)
    pdf.cell(50, 10, txt=f"Total pagado: {monto} Bs")
    pdf.ln(20)
    pdf.cell(50, 10, txt="Firma del usuario: ___________________")
    pdf.ln(10)
    pdf.cell(50, 10, txt="EPSA Municipal")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name