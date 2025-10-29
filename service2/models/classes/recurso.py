from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from models.exceptions import ValidationError

@dataclass
class Recurso:
    id: int
    nombre: str
    abreviatura: str
    metrica: str
    tipo: str # "Hardware" | "Software"
    valorXhora: float

    def __post_init__(self):
        self.tipo = self.tipo.capitalize()
        if self.tipo not in ["Hardware", "Software"]:
            raise ValidationError(f"Tipo de recurso inválido '{self.tipo}'.")


    def to_xml_element(self) -> ET.Element:
        el = ET.Element("recurso", {"id": str(self.id)})
        ET.SubElement(el, "nombre").text = self.nombre
        ET.SubElement(el, "abreviatura").text = self.abreviatura
        ET.SubElement(el, "metrica").text = self.metrica
        ET.SubElement(el, "tipo").text = self.tipo
        ET.SubElement(el, "valorXhora").text = str(self.valorXhora)
        return el

    @staticmethod
    def get_dict_recursos() -> Dict[int, Recurso]:
        tree = ET.parse("data/recursos.xml")
        root = tree.getroot()
        recursos = {}
        for r in root.findall("recurso"):
            rec = Recurso.from_element(r)
            recursos[rec.id] = rec
        return recursos
 

    @staticmethod
    def from_element(el: ET.Element) -> "Recurso":
        return Recurso(
            id=int(el.attrib["id"]),
            nombre=el.findtext("nombre", ""),
            abreviatura=el.findtext("abreviatura", ""),
            metrica=el.findtext("metrica", ""),
            tipo=el.findtext("tipo", ""),
            valorXhora=float(el.findtext("valorXhora", "0") or 0),
        )

    @staticmethod
    def write_xml(recursos: List["Recurso"]):
        root = ET.Element("listaRecursos")
        for recurso in recursos:
            root.append(recurso.to_xml_element())

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write("data/recursos.xml", encoding="utf-8", xml_declaration=True)

