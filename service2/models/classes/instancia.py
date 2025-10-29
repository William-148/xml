from __future__ import annotations
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from models.classes.fecha import Fecha
from models.exceptions import ValidationError

@dataclass(init=False)
class Instancia:
    id: int
    idConfiguracion: int
    nombre: str
    fechaInicio: Fecha
    estado: str = "Vigente"  # "Vigente" | "Cancelada"
    fechaFinal: Optional[Fecha]

    def __init__(self, id, idConfiguracion, nombre, fechaInicio, estado, fechaFinal):
        self.id = id
        self.idConfiguracion = idConfiguracion
        self.nombre = nombre
        self.fechaInicio = Fecha(fechaInicio)
        self.estado = estado.capitalize()
        self.fechaFinal = Fecha(fechaFinal) if fechaFinal != "" else None
        self.check_state()

    def check_state(self):
        if self.estado not in ["Vigente", "Cancelada"]:
            raise ValidationError(f"Estado de instancia inválido '{self.estado}'.")
        if self.estado == "Cancelada" and not self.fechaFinal:
            raise ValidationError("Una instancia cancelada debe tener una fecha final.")
        if self.estado == "Vigente":
            self.fechaFinal = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "idConfiguracion": self.idConfiguracion,
            "nombre": self.nombre,
            "fechaInicio": str(self.fechaInicio),
            "estado": self.estado,
            "fechaFinal": str(self.fechaFinal) if self.fechaFinal else None,
        }


    def to_xml_element(self) -> ET.Element:
        el = ET.Element("instancia", {"id": str(self.id)})
        ET.SubElement(el, "idConfiguracion").text = str(self.idConfiguracion)
        ET.SubElement(el, "nombre").text = self.nombre
        ET.SubElement(el, "fechaInicio").text = str(self.fechaInicio)
        ET.SubElement(el, "estado").text = self.estado
        ET.SubElement(el, "fechaFinal").text = str(self.fechaFinal) if self.fechaFinal else " "
        return el

    @staticmethod
    def from_element(el: ET.Element) -> "Instancia":
        return Instancia(
            id = int(el.attrib["id"]),
            idConfiguracion = int(el.findtext("idConfiguracion", "0")),
            nombre = el.findtext("nombre", ""),
            fechaInicio =el.findtext("fechaInicio", ""),
            estado = el.findtext("estado", "Vigente"),
            fechaFinal = el.findtext("fechaFinal", "").strip(),
        )

