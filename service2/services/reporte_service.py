from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Tuple
from models.classes.consumo import GrupoConsumos, Consumo
from models.classes.factura import Factura
from models.classes.detalle_factura import DetalleFactura, ConsumoFactura
from models.classes.recurso import Recurso
from models.classes.categoria import Categoria, GestorCategoria
from models.classes.cliente import Cliente
from models.classes.configuracion import Configuracion
from models.classes.factura import Factura

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ReporteService:

    def __init__(self, fecha_inicio: str, fecha_fin: str):
        self.base_path = "data/pdfs"
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        self.fecha_fin = datetime.strptime(fecha_fin, "%d/%m/%Y")
        self.facturas = Factura.get_all()

    def reporte1(self):
        gestor_categoria = GestorCategoria()
        categoria, config = self._generar_datos_reporte1(gestor_categoria)
 
        # Crear el documento PDF
        fecha_inicio_str = self.fecha_inicio.strftime('%d%m%Y')
        fecha_fin_str = self.fecha_fin.strftime('%d%m%Y')
        filename = f"{self.base_path}/reporte_ingresos_por_categoria.pdf"

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            title=f"Reporte Categoría {fecha_inicio_str}-{fecha_fin_str}",
            author="Tecnologías Chapinas S.A.",
            topMargin=0.5*inch
        )

        # Lista de elementos para el PDF
        elements = []
        # Estilos
        styles = getSampleStyleSheet()

        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
 
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20
        )

        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333')
        )

        # Título del reporte
        title = Paragraph("REPORTE DE INGRESOS POR CATEGORÍA Y CONFIGURACIÓN", title_style)
        elements.append(title)

        # Rango de fechas
        fecha_texto = f"Período: {self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')}"
        fecha_paragraph = Paragraph(fecha_texto, normal_style)
        elements.append(fecha_paragraph)
        elements.append(Spacer(1, 20))

        # SECCIÓN DE CATEGORÍAS
        cat_title = Paragraph("TOP CATEGORÍAS POR INGRESOS", subtitle_style)
        elements.append(cat_title)

        if categoria:
            # Preparar datos para la tabla de categorías
            cat_data = [['Posición', 'Categoría', 'Descripción', 'Ingresos (Q)']]

            for i, (cat_id, monto) in enumerate(categoria[:10], 1):  # Top 10 categorías
                cat_obj = gestor_categoria.get_categoria_by_id(cat_id)
                if cat_obj:
                    cat_data.append([
                        str(i),
                        cat_obj.nombre,
                        cat_obj.descripcion[:50] + "..." if len(cat_obj.descripcion) > 50 else cat_obj.descripcion,
                        f"Q {monto:,.2f}"
                    ])

            # Crear tabla de categorías
            cat_table = Table(cat_data, colWidths=[0.6*inch, 1.5*inch, 2.5*inch, 1.2*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))

            elements.append(cat_table)
        else:
            no_data = Paragraph("No hay datos de categorías para el período seleccionado.", normal_style)
            elements.append(no_data)

        elements.append(Spacer(1, 30))

        # SECCIÓN DE CONFIGURACIONES
        config_title = Paragraph("TOP CONFIGURACIONES POR INGRESOS", subtitle_style)
        elements.append(config_title)

        if config:
            # Preparar datos para la tabla de configuraciones
            config_data = [['Posición', 'Configuración', 'Categoría', 'Descripción', 'Ingresos (Q)']]

            for i, (config_id, monto) in enumerate(config[:10], 1):  # Top 10 configuraciones
                config_obj = gestor_categoria.get_config_by_id(config_id)
                cat_id = gestor_categoria.get_categoria_id_by_config_id(config_id)
                cat_obj = gestor_categoria.get_categoria_by_id(cat_id) if cat_id else None

                if config_obj and cat_obj:
                    config_data.append([
                        str(i),
                        config_obj.nombre,
                        cat_obj.nombre,
                        config_obj.descripcion[:40] + "..." if len(config_obj.descripcion) > 40 else config_obj.descripcion,
                        f"Q {monto:,.2f}"
                    ])

            # Crear tabla de configuraciones
            config_table = Table(config_data, colWidths=[0.6*inch, 1.3*inch, 1.3*inch, 2.0*inch, 1.2*inch])
            config_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))

            elements.append(config_table)
        else:
            no_data = Paragraph("No hay datos de configuraciones para el período seleccionado.", normal_style)
            elements.append(no_data)

        # Pie de página con estadísticas
        elements.append(Spacer(1, 30))
        total_cat = sum(monto for _, monto in categoria) if categoria else 0
        total_config = sum(monto for _, monto in config) if config else 0

        stats_text = f"""
        <b>Resumen Estadístico:</b><br/>
        Total ingresos por categorías: Q {total_cat:,.2f}<br/>
        Total ingresos por configuraciones: Q {total_config:,.2f}<br/>
        Categorías analizadas: {len(categoria)}<br/>
        Configuraciones analizadas: {len(config)}<br/>
        Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """

        stats_paragraph = Paragraph(stats_text, normal_style)
        elements.append(stats_paragraph)

        # Generar el PDF
        doc.build(elements)

        return filename

    def reporte2(self):
        recursos = Recurso.get_dict_recursos()
        ingresos_por_recurso = self._generar_datos_reporte2(recursos)

        # Crear el documento PDF
        fecha_inicio_str = self.fecha_inicio.strftime('%d%m%Y')
        fecha_fin_str = self.fecha_fin.strftime('%d%m%Y')

        filename = f"{self.base_path}/reporte_ingresos_recursos.pdf"

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            title=f"Reporte Recursos {fecha_inicio_str}-{fecha_fin_str}",
            author="Tecnologías Chapinas S.A.",

            topMargin=0.5*inch
        )

        # Lista de elementos para el PDF
        elements = []

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E4057'),
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20
        )

        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333')
        )

        # Estilo para destacados
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2E4057'),
            backColor=colors.HexColor('#F0F7FF'),
            borderPadding=5,
            borderColor=colors.HexColor('#2E4057'),
            borderWidth=1
        )

        # Título del reporte
        title = Paragraph("REPORTE DE INGRESOS POR RECURSOS", title_style)
        elements.append(title)

        # Rango de fechas
        fecha_texto = f"Período: {self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')}"
        fecha_paragraph = Paragraph(fecha_texto, normal_style)
        elements.append(fecha_paragraph)
        elements.append(Spacer(1, 20))

        # SECCIÓN PRINCIPAL DE RECURSOS
        recursos_title = Paragraph("TOP RECURSOS POR INGRESOS GENERADOS", subtitle_style)
        elements.append(recursos_title)

        if ingresos_por_recurso:
            # Preparar datos para la tabla de recursos
            recursos_data = [['Posición', 'Recurso', 'Abreviatura', 'Tipo', 'Métrica', 'Valor x Hora', 'Ingresos Totales (Q)']]

            total_ingresos = 0
            for i, (recurso_id, monto) in enumerate(ingresos_por_recurso[:15], 1):  # Top 15 recursos
                recurso_obj = recursos.get(recurso_id)
                if recurso_obj:
                    total_ingresos += monto
                    # Color diferente para Hardware vs Software
                    tipo_color = colors.HexColor('#4A6572') if recurso_obj.tipo == 'Hardware' else colors.HexColor('#2E4057')

                    recursos_data.append([
                        str(i),
                        recurso_obj.nombre,
                        recurso_obj.abreviatura,
                        recurso_obj.tipo,
                        recurso_obj.metrica,
                        f"Q {recurso_obj.valorXhora:,.2f}",
                        f"Q {monto:,.2f}"
                    ])

            # Crear tabla de recursos
            recursos_table = Table(recursos_data, colWidths=[0.6*inch, 1.5*inch, 0.8*inch, 0.9*inch, 0.9*inch, 1.2*inch, 1.3*inch])

            # Estilo de la tabla
            recursos_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                # Datos
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('ALIGN', (5, 1), (6, -1), 'RIGHT'),  # Alinear columnas monetarias a la derecha
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),

                # Colores por tipo de recurso
                ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor('#2E4057')),
                ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),

                # Filas alternadas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))

            elements.append(recursos_table)
            elements.append(Spacer(1, 20))

            # ESTADÍSTICAS DESTACADAS
            stats_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F7FF')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2E4057')),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2E4057')),
                ('PADDING', (0, 0), (-1, -1), 10),
            ])

            # Calcular estadísticas por tipo
            ingresos_hardware = sum(monto for recurso_id, monto in ingresos_por_recurso 
                                if recursos.get(recurso_id) and recursos[recurso_id].tipo == 'Hardware')
            ingresos_software = sum(monto for recurso_id, monto in ingresos_por_recurso 
                                if recursos.get(recurso_id) and recursos[recurso_id].tipo == 'Software')

            stats_data = [
                ['ESTADÍSTICAS PRINCIPALES'],
                [f'Ingresos Totales: Q {total_ingresos:,.2f}'],
                [f'Hardware: Q {ingresos_hardware:,.2f} | Software: Q {ingresos_software:,.2f}'],
                [f'Recursos Analizados: {len(ingresos_por_recurso)}']
            ]

            stats_table = Table(stats_data, colWidths=[6*inch])
            stats_table.setStyle(stats_style)
            elements.append(stats_table)

        else:
            no_data = Paragraph("No hay datos de ingresos por recursos para el período seleccionado.", normal_style)
            elements.append(no_data)

        elements.append(Spacer(1, 20))

        # ANÁLISIS ADICIONAL POR TIPO
        if ingresos_por_recurso:
            analisis_title = Paragraph("ANÁLISIS POR TIPO DE RECURSO", subtitle_style)
            elements.append(analisis_title)

            # Calcular porcentajes
            total = sum(monto for _, monto in ingresos_por_recurso)
            recursos_por_tipo = {}

            for recurso_id, monto in ingresos_por_recurso:
                recurso_obj = recursos.get(recurso_id)
                if recurso_obj:
                    tipo = recurso_obj.tipo
                    if tipo not in recursos_por_tipo:
                        recursos_por_tipo[tipo] = {'ingresos': 0, 'cantidad': 0}
                    recursos_por_tipo[tipo]['ingresos'] += monto
                    recursos_por_tipo[tipo]['cantidad'] += 1

            # Tabla de análisis por tipo
            analisis_data = [['Tipo', 'Cantidad de Recursos', 'Ingresos Totales (Q)', 'Porcentaje']]

            for tipo, datos in recursos_por_tipo.items():
                porcentaje = (datos['ingresos'] / total) * 100 if total > 0 else 0
                analisis_data.append([
                    tipo,
                    str(datos['cantidad']),
                    f"Q {datos['ingresos']:,.2f}",
                    f"{porcentaje:.1f}%"
                ])

            analisis_table = Table(analisis_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            analisis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6572')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))

            elements.append(analisis_table)

        # Pie de página
        elements.append(Spacer(1, 20))
        footer_text = f"Reporte generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
        footer_paragraph = Paragraph(footer_text, normal_style)
        elements.append(footer_paragraph)

        # Generar el PDF
        doc.build(elements)

        return filename

 
    # ------------------------------
    # MÉTODOS AUXILIARES
    # ------------------------------
    def _generar_datos_reporte1(self, gestor_categoria: GestorCategoria):
        """
            En la factura, el subtotal de una instancia corresponde a la sumatoria de los
            recursos consumidos de una configuración.
            - Agrupar cada subtotal por configuración (mediante su id) y sumarlos. Luego
              ordenarlos de mayor a menor para saber cuáles son las configuraciones más rentables.
            - Buscar a que Categoria pertenece cada configuración y agrupar los totales por Categoría.
        """
        facturas_filtradas = self._filtrar_facturas()
        grupo_conf: Dict[int, float] = {} # [id_configuracion] = sumatoria_subtotal
 
        # Agrupando y sumando subtotales por configuración
        for factura in facturas_filtradas:
            for detalle in factura.detalles:
                if detalle.idConfiguracion not in grupo_conf:
                    grupo_conf[detalle.idConfiguracion] = detalle.subtotal
                else:
                    grupo_conf[detalle.idConfiguracion] += detalle.subtotal
        # Ordenando de mayor a menor
        config_desc = sorted(grupo_conf.items(), key=lambda item: item[1], reverse=True)

        # Buscando categorías y agrupando totales por categoría
        grupo_categoria: Dict[int, float] = {} # [id_categoria] = sumatoria_subtotal
        for idConfiguracion, total in config_desc:
            id_categoria = gestor_categoria.get_categoria_id_by_config_id(idConfiguracion)
            if id_categoria is None:
                continue
            if id_categoria not in grupo_categoria:
                grupo_categoria[id_categoria] = total
            else:
                grupo_categoria[id_categoria] += total
        # Ordenando de mayor a menor
        categoria_desc = sorted(grupo_categoria.items(), key=lambda item: item[1], reverse=True)

        return (categoria_desc, config_desc)


    def _generar_datos_reporte2(self, recursos: Dict[int, Recurso]):
        facturas_filtradas = self._filtrar_facturas()

        # Agrupar aportes por recurso
        grupo_recursos: Dict[int, float] = {} # [id_recurso] = aporte_total
        for factura in facturas_filtradas:
            for detalle in factura.detalles:
               for rid, cantidad in detalle.recursos_cantidad.items():
                    recurso = recursos.get(rid)
                    if recurso is None:
                        continue
                    precio = recurso.valorXhora
                    aporte = cantidad * precio * detalle.horas
                    if rid not in grupo_recursos:
                        grupo_recursos[rid] = aporte
                    else:
                        grupo_recursos[rid] += aporte
        # Ordenando de mayor a menor
        return sorted(grupo_recursos.items(), key=lambda item: item[1], reverse=True)

    def _filtrar_facturas(self) -> List[Factura]:
        facturas_filtradas = []
        for item in self.facturas:
            fecha = datetime.strptime(item.fechaEmision, "%d/%m/%Y")
            if self.fecha_inicio <= fecha <= self.fecha_fin:
                facturas_filtradas.append(item)
        return facturas_filtradas



