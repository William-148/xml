from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.classes.configuracion import Configuracion
import xml.etree.ElementTree as ET

@dataclass
class Categoria:
    id: int
    nombre: str
    descripcion: str
    cargaTrabajo: str
    configuraciones: List[Configuracion] = field(default_factory=list)

    def to_xml_element(self) -> ET.Element:
        el = ET.Element("categoria", {"id": str(self.id)})
        ET.SubElement(el, "nombre").text = self.nombre
        ET.SubElement(el, "descripcion").text = self.descripcion
        ET.SubElement(el, "cargaTrabajo").text = self.cargaTrabajo
        lista_conf = ET.SubElement(el, "listaConfiguraciones")
        for c in self.configuraciones:
            lista_conf.append(c.to_xml_element())
        return el

    def to_dict(self) -> Dict[str, Optional[object]]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "cargaTrabajo": self.cargaTrabajo,
            "configuraciones": [c.to_dict() for c in self.configuraciones]
        }

    @staticmethod
    def from_element(el: ET.Element) -> "Categoria":
        # Creando objeto principal
        category = Categoria(
            id = int(el.attrib["id"]),
            nombre = el.findtext("nombre", ""),
            descripcion = el.findtext("descripcion", ""),
            cargaTrabajo = el.findtext("cargaTrabajo", "")
        )
 
        # Creando y agregando hijos (configuraciones)
        configs = []
        configuration_list = el.find('listaConfiguraciones')
        if configuration_list is not None:
            for configuration in configuration_list.findall('configuracion'):
                config = Configuracion.from_element(configuration)
                configs.append(config)

        category.configuraciones = configs
        return category

    @staticmethod
    def write_xml(categorias: List[Categoria]):
        root = ET.Element("listaCategorias")
        for categoria in categorias:
            root.append(categoria.to_xml_element())

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write("data/categorias.xml", encoding="utf-8", xml_declaration=True)

    @staticmethod
    def get_dict_categorias() -> Dict[int, Dict[str, Optional[object]]]:
        """
        Carga todas las categorias y devuelve un diccionario
        {id_categoria: diccionario}.
        """
        tree = ET.parse("data/categorias.xml")
        root = tree.getroot()
        categorias = {}
        for cat_el in root.findall("categoria"):
            cat = Categoria.from_element(cat_el)
            categorias[cat.id] = cat.to_dict()
        return categorias

    @staticmethod
    def get_dict_configuraciones() -> Dict[int, Configuracion]:
        """
        Carga todas las configuraciones y devuelve un diccionario
        {id_configuracion: Configuracion}.
        """
        tree = ET.parse("data/categorias.xml")
        root = tree.getroot()
        configs = {}
        for cat_el in root.findall("categoria"):
            cat = Categoria.from_element(cat_el)
            for conf in cat.configuraciones:
                configs[conf.id] = conf
        return configs


