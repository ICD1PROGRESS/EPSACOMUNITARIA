# src/utils/recibo_pdf.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pathlib import Path
from datetime import date, timedelta


# ===================================================================
# FUNCIONES AUXILIARES
# ===================================================================

def numero_a_letras(numero):
    """
    Convierte un número a letras en español (simplificado).
    Para montos decimales: 'Ciento veinte 50/100 BOLIVIANOS'
    """
    if numero is None or numero == 0:
        return "CERO 00/100 BOLIVIANOS"
    
    unidades = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
    decenas = ["", "DIEZ", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
    especiales = {11: "ONCE", 12: "DOCE", 13: "TRECE", 14: "CATORCE", 15: "QUINCE",
                  16: "DIECISEIS", 17: "DIECISIETE", 18: "DIECIOCHO", 19: "DIECINUEVE"}
    centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
    
    def convertir_entero(n):
        if n == 0:
            return "CERO"
        if n == 100:
            return "CIEN"
        if n < 10:
            return unidades[n]
        if 10 < n < 20:
            return especiales.get(n, "")
        if n < 100:
            d, u = divmod(n, 10)
            if u == 0:
                return decenas[d]
            return f"{decenas[d]} Y {unidades[u]}"
        if n < 1000:
            c, resto = divmod(n, 100)
            if resto == 0:
                return centenas[c]
            return f"{centenas[c]} {convertir_entero(resto)}"
        if n < 1000000:
            m, resto = divmod(n, 1000)
            if m == 1:
                prefijo = "MIL"
            else:
                prefijo = f"{convertir_entero(m)} MIL"
            if resto == 0:
                return prefijo
            return f"{prefijo} {convertir_entero(resto)}"
        return str(n)
    
    entero = int(numero)
    decimal = int(round((numero - entero) * 100))
    
    letras = convertir_entero(entero)
    return f"{letras} {decimal:02d}/100 BOLIVIANOS"


def generar_recibo_pdf(usuario, datos_recibo, config_epsa=None):
    """
    Genera un recibo en PDF estilo 'hoja recibo' del macro EPSACOL.
    
    datos_recibo: dict con toda la información de la transacción.
    config_epsa: objeto ConfiguracionEPSA (opcional, para logo y membrete).
    """
    output_dir = Path("recibos")
    output_dir.mkdir(exist_ok=True)
    
    nombre_archivo = f"recibo_{datos_recibo['codigo']}_{datos_recibo['fecha'].strftime('%Y%m%d')}_{datos_recibo['nro_recibo']}.pdf"
    ruta = output_dir / nombre_archivo

    doc = SimpleDocTemplate(
        str(ruta),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle(
        'TituloRecibo',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor('#1a5276'),
        fontName='Helvetica-Bold'
    )
    
    style_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor('#5d6d7e')
    )
    
    style_seccion = ParagraphStyle(
        'Seccion',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#1a5276'),
        spaceAfter=4,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    style_label = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#5d6d7e'),
        fontName='Helvetica-Bold'
    )
    
    style_valor = ParagraphStyle(
        'Valor',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    style_total = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1a5276'),
        fontName='Helvetica-Bold'
    )
    
    style_son = ParagraphStyle(
        'Son',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica-Oblique'
    )
    
    style_firma = ParagraphStyle(
        'Firma',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#5d6d7e'),
        fontName='Helvetica'
    )

    story = []
    
    # ===================================================================
    # ENCABEZADO: LOGO + TÍTULO + N° RECIBO
    # ===================================================================
    logo_img = None
    if config_epsa and config_epsa.logo_path:
        logo_path = Path(config_epsa.logo_path)
        if logo_path.exists():
            try:
                logo_img = Image(str(logo_path), width=1.2*inch, height=1.0*inch)
            except Exception:
                logo_img = None
    
    # Membrete
    membrete = ""
    if config_epsa and config_epsa.membrete_texto:
        membrete = config_epsa.membrete_texto
    else:
        membrete = "EPSA MUNICIPAL"
    
    # Tabla de encabezado: [Logo | Título + Membrete | N° Recibo]
    titulo_central = Paragraph(f"<b>{membrete}</b><br/><font size=14 color='#1a5276'>R E C I B O   O F I C I A L</font>", style_subtitulo)
    nro_recibo_text = Paragraph(f"<b>RECIBO N°:</b><br/><font size=14>{datos_recibo['nro_recibo']}</font>", style_valor)
    
    header_data = []
    if logo_img:
        header_data.append([logo_img, titulo_central, nro_recibo_text])
    else:
        header_data.append(["", titulo_central, nro_recibo_text])
    
    t_header = Table(header_data, colWidths=[1.5*inch, 4.0*inch, 2.0*inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))
    
    # Línea separadora
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a5276')))
    story.append(Spacer(1, 8))
    
    # ===================================================================
    # DATOS DEL CLIENTE (2 columnas: izquierda y derecha)
    # ===================================================================
    story.append(Paragraph("DATOS DEL CLIENTE", style_seccion))
    
    fecha_emision = datos_recibo['fecha'].strftime('%d/%m/%Y')
    
    # CORRECCIÓN: Fecha de vencimiento = fecha emisión + 30 días (usando timedelta)
    fecha_venc = datos_recibo['fecha'] + timedelta(days=30)
    fecha_venc_str = fecha_venc.strftime('%d/%m/%Y')
    
    # Izquierda: Código, Nombre, CI, Zona
    # Derecha: Fecha emisión, Periodo, Fecha vencimiento, Medidor
    datos_izq = [
        [Paragraph("<b>Código de usuario:</b>", style_label), 
         Paragraph(datos_recibo['codigo'], style_valor)],
        [Paragraph("<b>Nombre de usuario:</b>", style_label), 
         Paragraph(datos_recibo['nombre'], style_valor)],
        [Paragraph("<b>NIT / C.I.:</b>", style_label), 
         Paragraph(datos_recibo['ci'], style_valor)],
        [Paragraph("<b>Zona / Dirección:</b>", style_label), 
         Paragraph(datos_recibo['zona'], style_valor)],
    ]
    
    datos_der = [
        [Paragraph("<b>Fecha de emisión:</b>", style_label), 
         Paragraph(fecha_emision, style_valor)],
        [Paragraph("<b>Período de pago:</b>", style_label), 
         Paragraph(datos_recibo['periodo'], style_valor)],
        [Paragraph("<b>Fecha de vencimiento:</b>", style_label), 
         Paragraph(fecha_venc_str, style_valor)],
        [Paragraph("<b>N° Medidor:</b>", style_label), 
         Paragraph(datos_recibo['medidor'], style_valor)],
    ]
    
    # Combinar en una tabla de 2 columnas
    filas_combinadas = []
    for i in range(max(len(datos_izq), len(datos_der))):
        izq = datos_izq[i] if i < len(datos_izq) else ["", ""]
        der = datos_der[i] if i < len(datos_der) else ["", ""]
        filas_combinadas.append([izq[0], izq[1], der[0], der[1]])
    
    t_cliente = Table(filas_combinadas, colWidths=[1.6*inch, 2.4*inch, 1.6*inch, 2.4*inch])
    t_cliente.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#d5d8dc')),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.HexColor('#d5d8dc')),
    ]))
    story.append(t_cliente)
    story.append(Spacer(1, 12))
    
    # ===================================================================
    # SECCIÓN: CONSUMO DE AGUA (solo si NO es deuda específica)
    # ===================================================================
    if not datos_recibo.get('es_deuda_especifica', False):
        story.append(Paragraph("CONSUMO DE AGUA", style_seccion))
        
        lect_ant = datos_recibo.get('lectura_anterior', 0)
        lect_act = datos_recibo.get('lectura_actual', 0)
        consumo = datos_recibo.get('consumo', 0)
        
        data_consumo = [
            [Paragraph("<b>Lectura anterior:</b>", style_label), 
             Paragraph(f"{lect_ant}" if lect_ant != "-" else "-", style_valor), "", ""],
            [Paragraph("<b>Lectura actual:</b>", style_label), 
             Paragraph(f"{lect_act}" if lect_act != "-" else "-", style_valor), "", ""],
            [Paragraph("<b>Consumo del período (m³):</b>", style_label), 
             Paragraph(f"{consumo}" if consumo != "-" else "-", style_valor), "", ""],
        ]
        
        t_consumo = Table(data_consumo, colWidths=[2.0*inch, 2.0*inch, 2.0*inch, 2.0*inch])
        t_consumo.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#d5d8dc')),
            ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.HexColor('#d5d8dc')),
        ]))
        story.append(t_consumo)
        story.append(Spacer(1, 12))
    
    # ===================================================================
    # SECCIÓN: DETALLE DE PAGO
    # ===================================================================
    story.append(Paragraph("DETALLE DE PAGO", style_seccion))
    
    importe_consumo = datos_recibo.get('importe_consumo', 0)
    reconexion = datos_recibo.get('reconexion', 0)
    deuda = datos_recibo.get('deuda', 0)
    total = datos_recibo.get('total', 0)
    
    # Determinar etiqueta según tipo de recibo
    if datos_recibo.get('es_deuda_especifica', False):
        label_concepto = f"Pago de Deuda - Período {datos_recibo['periodo']}"
    else:
        label_concepto = "Importe total por consumo:"
    
    data_pago = [
        [Paragraph(f"<b>{label_concepto}</b>", style_label), 
         Paragraph(f"{importe_consumo:.2f} Bs", style_valor)],
    ]
    
    if reconexion > 0:
        data_pago.append([
            Paragraph("<b>Conexión / Reconexión:</b>", style_label),
            Paragraph(f"{reconexion:.2f} Bs", style_valor)
        ])
    
    if deuda > 0 and not datos_recibo.get('es_deuda_especifica', False):
        data_pago.append([
            Paragraph("<b>Pago pendiente (deuda anterior):</b>", style_label),
            Paragraph(f"{deuda:.2f} Bs", style_valor)
        ])
    
    # Fila TOTAL
    data_pago.append([
        Paragraph("<b>TOTAL A PAGAR (Bs):</b>", style_total),
        Paragraph(f"{total:.2f} Bs", style_total)
    ])
    
    t_pago = Table(data_pago, colWidths=[4.5*inch, 3.5*inch])
    t_pago.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-2), 8),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 12),
        ('TOPPADDING', (0,-1), (-1,-1), 8),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#d5d8dc')),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor('#1a5276')),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, colors.HexColor('#1a5276')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#eaf2f8')),
    ]))
    story.append(t_pago)
    story.append(Spacer(1, 10))
    
    # ===================================================================
    # SON: (monto en letras)
    # ===================================================================
    monto_en_letras = numero_a_letras(total)
    story.append(Paragraph(f"<b>Son:</b> {monto_en_letras}", style_son))
    story.append(Spacer(1, 20))
    
    # ===================================================================
    # EFECTIVO Y CAMBIO
    # ===================================================================
    efectivo = datos_recibo.get('efectivo', 0)
    cambio = datos_recibo.get('cambio', 0)
    
    if efectivo > 0:
        story.append(Paragraph(f"<b>Efectivo recibido:</b> {efectivo:.2f} Bs", style_valor))
        story.append(Paragraph(f"<b>Cambio:</b> {cambio:.2f} Bs", style_valor))
        story.append(Spacer(1, 16))
    
    # ===================================================================
    # FIRMAS
    # ===================================================================
    story.append(Spacer(1, 30))
    
    firma_data = [
        ["_______________________________", "_______________________________"],
        [Paragraph(f"<b>{datos_recibo['nombre']}</b><br/>USUARIO", style_firma),
         Paragraph(f"<b>{membrete}</b><br/>EPSA", style_firma)]
    ]
    
    t_firma = Table(firma_data, colWidths=[3.5*inch, 3.5*inch])
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('TOPPADDING', (0,1), (-1,1), 4),
    ]))
    story.append(t_firma)
    
    # ===================================================================
    # PIE DE PÁGINA
    # ===================================================================
    story.append(Spacer(1, 20))
    pie = config_epsa.direccion if (config_epsa and config_epsa.direccion) else ""
    if config_epsa and config_epsa.telefono:
        pie += f" | Tel: {config_epsa.telefono}"
    
    if pie:
        story.append(Paragraph(pie, ParagraphStyle(
            'Pie',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d')
        )))
    
    story.append(Paragraph(
        "Este documento es un comprobante oficial de pago. Conserve su recibo.",
        ParagraphStyle(
            'Legal',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#95a5a6')
        )
    ))
    
    # Construir PDF
    doc.build(story)
    return str(ruta)