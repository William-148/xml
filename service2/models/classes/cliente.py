from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List,Tuple, Optional
import xml.etree.ElementTree as ET
import re
import random
import string
from models.classes.instancia import Instancia
from models.exceptions import ValidationError

@dataclass
class Cliente:
    nit: str
    nombre: str
    usuario: str
    clave: str
    direccion: str
    correoElectronico: str
    instancias: List[Instancia] = field(default_factory=list)

    def __post_init__(self):
        self.validar_nit()

    def validar_nit(self):
        """
            Lanza una excepción {ValidationError} si el NIT no es válido.
        """
        patron = r'^\d+-[0-9Kk]$'
        if not re.match(patron, self.nit):
            raise ValidationError(f"NIT inválido '{self.nit}'. Formato permitido 1234567-0 o 1234567-K.")

    def to_dict(self) -> Dict:
        """
            Convierte el objeto Cliente a un diccionario. Sin incluir las instancias.
        """
        return {
            "nit": self.nit,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "clave": self.clave,
            "direccion": self.direccion,
            "correoElectronico": self.correoElectronico,
        }


    def to_xml_element(self) -> ET.Element:
        el = ET.Element("cliente", {"nit": self.nit})
        ET.SubElement(el, "nombre").text = self.nombre
        ET.SubElement(el, "usuario").text = self.usuario
        ET.SubElement(el, "clave").text = self.clave
        ET.SubElement(el, "direccion").text = self.direccion
        ET.SubElement(el, "correoElectronico").text = self.correoElectronico

        # Creando nodos listaInstancias
        lista = ET.SubElement(el, "listaInstancias")
        for inst in self.instancias:
            lista.append(inst.to_xml_element())
        return el

    @staticmethod
    def from_element(el: ET.Element) -> Tuple["Cliente", Optional[str]]:
        client = Cliente(
            nit = el.attrib["nit"],
            nombre = el.findtext("nombre", ""),
            usuario = el.findtext("usuario"),
            clave = el.findtext("clave"),
            direccion = el.findtext("direccion"),
            correoElectronico = el.findtext("correoElectronico")
        )

        instances = []
        errors = []
        instance_list = el.find("listaInstancias")
        if instance_list is not None:
            for nodo in instance_list.findall("instancia"):
                try:
                    instances.append(Instancia.from_element(nodo))
                except ValidationError as e:
                    errors.append(f"Error al procesar instancia: {e}")
 
        client.instancias = instances
        return client, "; ".join(errors) if len(errors) > 0 else None

    @staticmethod
    def write_xml(clientes: List["Cliente"]):
        root = ET.Element("listaClientes")
        for cliente in clientes:
            root.append(cliente.to_xml_element())

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write("data/clientes.xml", encoding="utf-8", xml_declaration=True)

    @staticmethod
    def get_all() -> List[Cliente]:
        try:
            tree = ET.parse("data/clientes.xml")
            root = tree.getroot()
            clientes = []
            for cli_el in root.findall("cliente"):
                cli, _ = Cliente.from_element(cli_el)
                clientes.append(cli)
            return clientes
        except Exception as e:
            print(f"Error inesperado al leer clientes.xml: {e}")
            return []
 

    @staticmethod
    def get_all_dict() -> Dict[str, Cliente]:
        try:
            tree = ET.parse("data/clientes.xml")
            root = tree.getroot()
            clientes = {}
            for cli_el in root.findall("cliente"):
                cli, _ = Cliente.from_element(cli_el)
                clientes[cli.nit] = cli
            return clientes
        except Exception as e:
            print(f"Error inesperado al leer clientes.xml: {e}")
            return {}


    @staticmethod
    def get_by_nit(nit_cliente:int) -> Optional[Cliente]:
        try:
            tree = ET.parse("data/clientes.xml")
            root: ET.Element = tree.getroot()
            resultado: Optional[ET.Element] = root.find(f".//cliente[@nit='{nit_cliente}']")
            if resultado is not None:
                cliente_obj, _ = Cliente.from_element(resultado)
                return cliente_obj
        except (FileNotFoundError, ET.ParseError):
            pass

        return None

    @staticmethod
    def add_cliente(nit: str, nombre: str, direccion: str, correoElectronico: str) -> None:
        clientes = Cliente.get_all()
        usuario = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        clave = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        nuevo_cliente = Cliente(
            nit=nit,
            nombre=nombre,
            usuario=usuario,
            clave=clave,
            direccion=direccion,
            correoElectronico=correoElectronico,
            instancias=[]
        )
        clientes.append(nuevo_cliente)
        Cliente.write_xml(clientes)

