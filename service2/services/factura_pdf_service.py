from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple
from models.classes.consumo import GrupoConsumos, Consumo
from models.classes.factura import Factura
from models.classes.detalle_factura import DetalleFactura, ConsumoFactura
from models.classes.recurso import Recurso
from models.classes.categoria import Categoria
from models.classes.cliente import Cliente
from models.classes.instancia import Instancia

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime


class FacturaPdfService:

    def __init__(self, id_factura: int):
        self.base_path = "data/pdfs"

        self.recursos = Recurso.get_dict_recursos()
        factura = Factura.get_by_id(id_factura)
        if not factura:
            raise ValueError(f"Factura con ID {id_factura} no encontrada.")

        cliente = Cliente.get_by_nit(factura.nitCliente)
        if not cliente:
            raise ValueError(f"Cliente con NIT {factura.nitCliente} no encontrado.")

        instancias_dict = {inst.id: inst for inst in cliente.instancias}

        self.factura = factura
        self.cliente = cliente
        self.instancias_dict = instancias_dict

    def generar_pdf(self):
        file_path = f"{self.base_path}/factura_{str(self.factura.id)}.pdf"

        # Configuración base del documento
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            title=f"Factura #{str(self.factura.id)}",
            author="Tecnologías Chapinas S.A.",
            rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Estilos personalizados
        styles.add(ParagraphStyle(name="Empresa", fontSize=14, textColor=colors.HexColor("#003366"), alignment=1, leading=16))
        styles.add(ParagraphStyle(name="Factura", fontSize=12, textColor=colors.gray, alignment=1))
        styles.add(ParagraphStyle(name="Subtitulo", fontSize=11, textColor=colors.HexColor("#003366"), leading=14, spaceAfter=6))
        styles.add(ParagraphStyle(name="Campo", fontSize=10, textColor=colors.black, leading=14))
        styles.add(ParagraphStyle(name="Total", fontSize=12, textColor=colors.HexColor("#003366"), leading=14))
        styles.add(ParagraphStyle(name="Footer", fontSize=8, textColor=colors.gray, alignment=2))

        elements = []

        # Encabezado elegante
        elements.append(Paragraph("Tecnologías Chapinas S.A.", styles["Empresa"]))
        elements.append(Paragraph(f"Factura #{str(self.factura.id)}", styles["Factura"]))
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#003366"), thickness=1, spaceBefore=8, spaceAfter=12))

        # Datos del cliente
        datos_cliente = f"""
            <b>Cliente:</b> {self.cliente.nombre}<br/>
            <b>NIT:</b> {self.cliente.nit}<br/>
            <b>Dirección:</b> {self.cliente.direccion}<br/>
            <b>Correo:</b> {self.cliente.correoElectronico}<br/>
            <b>Fecha de emisión:</b> {self.factura.fechaEmision}<br/>
            <b>Rango de inicio:</b> {self.factura.rango_inicio}<br/>
        """
        elements.append(Paragraph("<b>Datos del Cliente</b>", styles["Subtitulo"]))
        elements.append(Paragraph(datos_cliente, styles["Campo"]))
        elements.append(Spacer(1, 0.15 * inch))

        # Detalle de instancias
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#003366"), thickness=0.5, spaceBefore=6, spaceAfter=8))
        elements.append(Paragraph("<b>Detalle de Instancias</b>", styles["Subtitulo"]))

        for detalle in self.factura.detalles:
            inst = self.instancias_dict.get(detalle.idInstancia)
            if inst:
                elements.append(Paragraph(f"<b>Instancia:</b> {inst.nombre} (ID {inst.id})", styles["Campo"]))
                elements.append(Paragraph(f"<b>Horas facturadas:</b> {detalle.horas:.2f}", styles["Campo"]))
                elements.append(Paragraph(f"<b>Subtotal:</b> Q{detalle.subtotal:.2f}", styles["Campo"]))
                elements.append(Spacer(1, 0.1 * inch))

            # Tabla de consumos
            elements.append(Paragraph("Consumos", styles["Subtitulo"]))
            data_consumos = [["Fecha/Hora", "Tiempo (h)"]]
            for c in detalle.consumos:
                data_consumos.append([c.fechaHora, f"{c.tiempo:.2f}"])

            tabla_consumos = Table(data_consumos, colWidths=[3 * inch, 1.5 * inch])
            tabla_consumos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]))
            elements.append(tabla_consumos)
            elements.append(Spacer(1, 0.15 * inch))

            # Tabla de recursos
            elements.append(Paragraph("Recursos Asociados", styles["Subtitulo"]))
            data_recursos = [["Recurso", "Cantidad", "Precio/Hora", "Aporte (Q)"]]
            for rid, cantidad in detalle.recursos_cantidad.items():
                recurso = self.recursos[rid]
                if recurso is None:
                    continue
                precio = recurso.valorXhora
                aporte = cantidad * precio * detalle.horas
                data_recursos.append([
                    recurso.nombre,
                    f"{cantidad} {recurso.metrica}",
                    f"Q{precio:.2f}",
                    f"Q{aporte:.2f}"
                ])

            tabla_recursos = Table(data_recursos, colWidths=[3 * inch, 1 * inch, 1.2 * inch, 1.2 * inch])
            tabla_recursos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]))
            elements.append(tabla_recursos)
            elements.append(Spacer(1, 0.3 * inch))

        # Total
        elements.append(HRFlowable(width="100%", color=colors.HexColor("#003366"), thickness=1, spaceBefore=6, spaceAfter=8))
        elements.append(Paragraph(f"<b>Total a pagar:</b> Q{self.factura.total:.2f}", styles["Total"]))
        elements.append(Spacer(1, 0.3 * inch))

        # Pie de página
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Generado el {fecha_actual}", styles["Footer"]))

        doc.build(elements)
        return file_path

