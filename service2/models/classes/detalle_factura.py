from __future__ import annotations
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET


@dataclass
class DetalleFactura:
    """
    Representa el detalle de una factura (una línea por instancia).
    """
    idInstancia: int
    idConfiguracion: int
    horas: float
    subtotal: float
    recursos_cantidad: Dict[int, float] = field(default_factory=dict)
    consumos: List[ConsumoFactura] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "idInstancia": self.idInstancia,
            "idConfiguracion": self.idConfiguracion,
            "horas": self.horas,
            "subtotal": self.subtotal,
            "recursos": self.recursos_cantidad,
            "consumos": [consumo.to_dict() for consumo in self.consumos]
        }

    def to_xml_element(self) -> ET.Element:
        """
        Convierte el detalle en un elemento XML.
        """
        detalle_el = ET.Element("instancia", attrib={
            "id": str(self.idInstancia),
            "idConfiguracion": str(self.idConfiguracion),
            "horas": f"{self.horas:.2f}",
            "subtotal": f"Q{self.subtotal:.2f}"
        })
        ET.SubElement(detalle_el, "recursos").extend(self.recursos_to_xml_element())
        ET.SubElement(detalle_el, "consumos").extend(self.consumos_to_xml_element())
        return detalle_el

    def recursos_to_xml_element(self) -> ET.Element:
        recursos_el = ET.Element("recursos")
        for rid, cantidad in self.recursos_cantidad.items():
            recurso_el = ET.SubElement(recursos_el, "recurso", attrib={
                "id": str(rid),
                "cantidad": f"{cantidad:.2f}"
            })
        return recursos_el

    def consumos_to_xml_element(self) -> ET.Element:
        consumos_el = ET.Element("consumos")
        for consumo in self.consumos:
            consumos_el.append(consumo.to_xml_element())
        return consumos_el


    @staticmethod
    def from_element(element: ET.Element) -> DetalleFactura:
        id_instancia = int(element.get("id", "0"))
        id_configuracion = int(element.get("idConfiguracion", "0"))
        horas = float(element.get("horas", "0"))
        subtotal_str = element.get("subtotal", "Q0.00").replace("Q", "").strip()

        try:
            subtotal = float(subtotal_str)
        except ValueError:
            subtotal = 0.0

        recursos_cantidad: Dict[int, float] = {}
        recursos_el = element.find("recursos")
        if recursos_el is not None:
            for recurso_el in recursos_el.findall("recurso"):
                rid = int(recurso_el.get("id", "0"))
                cantidad = float(recurso_el.get("cantidad", "0"))
                recursos_cantidad[rid] = cantidad

        consumos: List[ConsumoFactura] = []
        consumos_el = element.find("consumos")
        if consumos_el is not None:
            for consumo_el in consumos_el.findall("consumo"):
                consumos.append(ConsumoFactura.from_element(consumo_el))

        return DetalleFactura(
            idInstancia=id_instancia,
            idConfiguracion=id_configuracion,
            horas=horas,
            subtotal=subtotal,
            recursos_cantidad=recursos_cantidad,
            consumos=consumos
        )

@dataclass
class ConsumoFactura:
    tiempo: float
    fechaHora: str

    def to_xml_element(self) -> ET.Element:
        return ET.Element("consumo", attrib={
            "tiempo": f"{self.tiempo:.2f}",
            "fechaHora": self.fechaHora
        })

    def to_dict(self) -> dict:
        return {
            "tiempo": self.tiempo,
            "fechaHora": self.fechaHora
        }

    @staticmethod
    def from_element(element: ET.Element) -> ConsumoFactura:
        tiempo = float(element.get("tiempo", "0"))
        fecha_hora = element.get("fechaHora", "")
        return ConsumoFactura(tiempo=tiempo, fechaHora=fecha_hora)


