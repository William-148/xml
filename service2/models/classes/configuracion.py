from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

@dataclass
class Configuracion:
    id: int
    nombre: str
    descripcion: str
    # recurso_id -> cantidad
    recursos: Dict[int, float] = field(default_factory=dict)

    def to_xml_element(self) -> ET.Element:
        el = ET.Element("configuracion", {"id": str(self.id)})
        ET.SubElement(el, "nombre").text = self.nombre
        ET.SubElement(el, "descripcion").text = self.descripcion
        recursos_el = ET.SubElement(el, "recursosConfiguracion")
        for rid, cantidad in self.recursos.items():
            rec_el = ET.SubElement(recursos_el, "recurso", {"id": str(rid)})
            rec_el.text = str(cantidad)
        return el

    def to_dict(self) -> Dict[str, Optional[object]]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "recursos": self.recursos
        }

    @staticmethod
    def from_element(el: ET.Element) -> "Configuracion":
        configuration = Configuracion(
            id=int(el.attrib["id"]),
            nombre=el.findtext("nombre", ""),
            descripcion=el.findtext("descripcion", "")
        )

        recursosConfiguracion = {}
        resource_config_list = el.find("recursosConfiguracion")
        if resource_config_list is not None:
            for r in resource_config_list.findall("recurso"):
                rid = int(r.attrib["id"])
                cantidad = float(r.text or "0")
                recursosConfiguracion[rid] = cantidad

        configuration.recursos = recursosConfiguracion
        return configuration

