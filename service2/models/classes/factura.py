from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import xml.etree.ElementTree as ET
import uuid
from pathlib import Path
from models.classes.detalle_factura import DetalleFactura


@dataclass
class Factura:
    id: int
    nitCliente: str
    fechaEmision: str
    rango_inicio: str
    detalles: List[DetalleFactura] = field(default_factory=list)
    total: float = 0.0

    @staticmethod
    def generar(nitCliente: str, rango_inicio: str, rango_fin: str, detalles: List[DetalleFactura], total: float) -> "Factura":
        """
        Crea una nueva factura con un ID único basado en el archivo existente.
        """
        nuevo_id = uuid.uuid4().int >> 64

        return Factura(
            id=nuevo_id,
            nitCliente=nitCliente,
            fechaEmision=rango_fin,
            rango_inicio=rango_inicio,
            detalles=detalles,
            total=round(total, 2)
        )

    def to_dict(self, incluir_detalles: bool = True) -> dict:
        return {
            "id": self.id,
            "nitCliente": self.nitCliente,
            "fechaEmision": self.fechaEmision,
            "rango_inicio": self.rango_inicio,
            "detalles": [detalle.to_dict() for detalle in self.detalles] if incluir_detalles else [],
            "total": self.total,
        }

    def to_xml_element(self) -> ET.Element:
        """
        Convierte la factura en un elemento XML.
        """
        factura_el = ET.Element("factura", attrib={
            "id": str(self.id),
            "nitCliente": self.nitCliente
        })
        ET.SubElement(factura_el, "fechaEmision").text = self.fechaEmision
        ET.SubElement(factura_el, "rangoInicio").text = self.rango_inicio
        detalle_el = ET.SubElement(factura_el, "detalles")
        for det in self.detalles:
            detalle_el.append(det.to_xml_element())

        ET.SubElement(factura_el, "total").text = f"Q{self.total:.2f}"
        return factura_el

    @staticmethod
    def from_element(element: ET.Element) -> "Factura":
        id_ = int(element.get("id", "0"))
        nit_cliente = element.get("nitCliente", "")
        fecha_emision = element.findtext("fechaEmision", "")
        rango_inicio = element.findtext("rangoInicio", "")
        total_str = element.findtext("total", "Q0.00").replace("Q", "").strip()

        try:
            total = float(total_str)
        except ValueError:
            total = 0.0

        detalles_el = element.find("detalles")
        detalles = []
        if detalles_el is not None:
            for det_el in detalles_el.findall("instancia"):
                detalles.append(DetalleFactura.from_element(det_el))

        return Factura(
            id=id_,
            nitCliente=nit_cliente,
            fechaEmision=fecha_emision,
            rango_inicio=rango_inicio,
            detalles=detalles,
            total=round(total, 2)
        )

    @staticmethod
    def get_all() -> Dict[int, Factura]:
        tree = ET.parse("data/facturas.xml")
        root = tree.getroot()
        facturas = []
        for r in root.findall("factura"):
            facturas.append(Factura.from_element(r))
        return facturas

    @staticmethod
    def get_by_id(factura_id: int) -> Optional[Factura]:
        """
        Busca y retorna una factura por su ID desde el archivo XML.
        """
        try:
            tree: ET.ElementTree = ET.parse("data/facturas.xml")
            root: ET.Element = tree.getroot()
            resultado: Optional[ET.Element] = root.find(f".//factura[@id='{factura_id}']")
            if resultado is not None:
                return Factura.from_element(resultado)
        except (FileNotFoundError, ET.ParseError):
            pass

        return None


    @staticmethod
    def write_xml(facturas: List["Factura"], ruta: Path = Path("data/facturas.xml")) -> None:
        """
        Guarda las facturas nuevas en el archivo XML, manteniendo las existentes.
        """
        try:
            tree = ET.parse(ruta)
            root = tree.getroot()
        except (FileNotFoundError, ET.ParseError):
            root = ET.Element("listaFacturas")

        for factura in facturas:
            root.append(factura.to_xml_element())

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        tree.write(ruta, encoding="utf-8", xml_declaration=True)
