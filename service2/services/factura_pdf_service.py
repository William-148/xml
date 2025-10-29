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
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER


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
        # Nombre de archivo
        file_path = f"{self.base_path}/factura_{str(self.factura.id)}.pdf"

        # Configuración
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            title=f"Factura #{str(self.factura.id)}",
            author="Tecnologías Chapinas S.A."
        )
        styles = getSampleStyleSheet()
        elements = []
        # Encabezado
        title = Paragraph(
            f"<b>Factura #{str(self.factura.id)}</b><br/>"
            f"Tecnologías Chapinas S.A.",
            styles["Title"]
        )
        elements.append(title)
        elements.append(Spacer(1, 0.25 * inch))
        # Datos generales
        datos_cliente = f"""
        <b>Cliente:</b> {self.cliente.nombre}<br/>
        <b>NIT:</b> {self.cliente.nit}<br/>
        <b>Dirección:</b> {self.cliente.direccion}<br/>
        <b>Correo:</b> {self.cliente.correoElectronico}<br/>
        <b>Fecha emisión:</b> {self.factura.fechaEmision}<br/>
        <b>Rango inicio:</b> {self.factura.rango_inicio}<br/>
        """
        elements.append(Paragraph(datos_cliente, styles["Normal"]))
        elements.append(Spacer(1, 0.25 * inch))

        # Tabla de detalle de instancias
        elements.append(Paragraph("<b>Detalle de Instancias</b>", styles["Heading2"]))
        for detalle in self.factura.detalles:
            inst = self.instancias_dict[detalle.idInstancia]
            if inst is not None:
                elements.append(Paragraph(f"<b>Instancia:</b> {inst.nombre} (ID {str(inst.id)})", styles["Normal"]))
                elements.append(Paragraph(f"<b>Horas facturadas:</b> {detalle.horas:.2f}", styles["Normal"]))
                elements.append(Paragraph(f"<b>Subtotal:</b> Q{detalle.subtotal:.2f}", styles["Normal"]))
                elements.append(Spacer(1, 0.1 * inch))

            # Tabla de consumos
            elements.append(Paragraph("<b>Consumos:</b>", styles["Normal"]))
            data_consumos = [["Fecha/Hora", "Tiempo (h)"]]
            for c in detalle.consumos:
                data_consumos.append([str(c.fechaHora), f"{c.tiempo:.2f}"])
            tabla_consumos = Table(data_consumos, colWidths=[3*inch, 1.5*inch])
            tabla_consumos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            elements.append(tabla_consumos)
            elements.append(Spacer(1, 0.15 * inch))
            # Tabla de recursos de la configuración
            elements.append(Paragraph("<b>Recursos asociados:</b>", styles["Normal"]))
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
            tabla_recursos = Table(data_recursos, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            tabla_recursos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ]))
            elements.append(tabla_recursos)
            elements.append(Spacer(1, 0.25 * inch))

        # Total general
        elements.append(Paragraph(f"<b>Total a pagar:</b> Q{self.factura.total:.2f}", styles["Heading2"]))
        elements.append(Spacer(1, 0.25 * inch))
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"<font size=8>Generado el {fecha_actual}</font>", styles["Normal"]))

        # Generar PDF
        doc.build(elements)
        return file_path

