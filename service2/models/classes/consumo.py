from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from models.classes.fecha_hora import FechaHora
from models.exceptions import ValidationError
import re


@dataclass
class GrupoConsumos:
    nitCliente: str
    idInstancia: int
    consumos: List[Consumo] = field(default_factory=list)

    def __post_init__(self):
        self.validar_nit()

    def validar_nit(self):
        """
            Lanza una excepción {ValidationError} si el NIT no es válido.
        """
        patron = r'^\d+-[0-9Kk]$'
        if not re.match(patron, self.nitCliente):
            raise ValidationError(f"NIT inválido '{self.nitCliente}'.")

    def to_xml_element(self) -> ET.Element:
        grupo_elem = ET.Element("grupoConsumos", attrib={
            "nitCliente": self.nitCliente,
            "idInstancia": str(self.idInstancia)
        })

        for consumo in self.consumos:
            grupo_elem.append(consumo.to_xml_element())

        return grupo_elem

    @staticmethod
    def write_xml(gruposComsumos: List["GrupoConsumos"]):
        root = ET.Element("listadoConsumos")
        for grupoComsumos in gruposComsumos:
            root.append(grupoComsumos.to_xml_element())

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write("data/consumos.xml", encoding="utf-8", xml_declaration=True)

    @staticmethod
    def append_xml(nuevos_grupos: List[GrupoConsumos]):
        try:
            tree = ET.parse("data/consumos.xml")
            root = tree.getroot()
        except (ET.ParseError, FileNotFoundError):
            root = ET.Element("listadoConsumos")

        grupos_existentes: Dict[Tuple[str, int], GrupoConsumos] = {}

        for grupo_elem in root.findall("grupoConsumos"):
            nit = grupo_elem.get("nitCliente")
            id_inst = int(grupo_elem.get("idInstancia"))
            grupo = GrupoConsumos(nitCliente=nit, idInstancia=id_inst)

            for consumo_elem in grupo_elem.findall("consumo"):
                grupo.consumos.append(Consumo.from_xml_element(consumo_elem))

            grupos_existentes[(nit, id_inst)] = grupo

        for nuevo in nuevos_grupos:
            clave = (nuevo.nitCliente, nuevo.idInstancia)
            if clave in grupos_existentes:
                grupos_existentes[clave].consumos.extend(nuevo.consumos)
            else:
                grupos_existentes[clave] = nuevo

        GrupoConsumos.write_xml(list(grupos_existentes.values()))

    def get_all() -> List[GrupoConsumos]:
        tree = ET.parse("data/consumos.xml")
        root = tree.getroot()
        grupos = []
        for grupo_el in root.findall("grupoConsumos"):
            nit = grupo_el.attrib["nitCliente"]
            id_inst = int(grupo_el.attrib["idInstancia"])
            grupo = GrupoConsumos(nitCliente=nit, idInstancia=id_inst)
            for consumo_el in grupo_el.findall("consumo"):
                grupo.consumos.append(Consumo.from_xml_element(consumo_el))
            grupos.append(grupo)
        return grupos



class Consumo:
    tiempo: float
    fechaHora: FechaHora
    facturado: bool = False

    def __init__(self, tiempo: float, fechaHora: str, facturado: bool = False):
        self.tiempo = tiempo
        self.fechaHora = FechaHora(fechaHora)
        self.facturado = facturado

    def to_xml_element(self) -> ET.Element:
        """
        Convierte el objeto Consumo en un elemento XML.
        """
        elem = ET.Element("consumo", attrib={
            "facturado": str(self.facturado).lower()
        })
        ET.SubElement(elem, "tiempo").text = str(self.tiempo)
        ET.SubElement(elem, "fechaHora").text = str(self.fechaHora)
        return elem

    @staticmethod
    def from_xml_element(elem: ET.Element) -> "Consumo":
        """
        Crea un objeto Consumo a partir de un elemento XML.
        """
        return Consumo(
            tiempo=float(elem.find("tiempo").text),
            fechaHora=elem.find("fechaHora").text,
            facturado=elem.get("facturado", "false").lower() == "true"
        )
