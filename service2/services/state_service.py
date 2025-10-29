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


class StateService:

    def get_app_state(self):
        recursos = Recurso.get_dict_recursos()
        categorias = Categoria.get_dict_categorias()
        facturas = Factura.get_all()
        clientes = Cliente.get_all()
        return {
            "recursos": recursos,
            "categorias": categorias,
            "facturas": facturas,
            "clientes": clientes
        }

    def get_recursos(self):
        return { "recursos": Recurso.get_dict_recursos() }

    def get_categorias(self):
        recursos = Recurso.get_dict_recursos()
        categorias = Categoria.get_dict_categorias()
        return {
            "recursos": recursos,
            "categorias": categorias,
        }

    def get_clientes(self):
        # facturas = Factura.get_all()
        clientes = Cliente.get_all()
        return {
            # "facturas": facturas,
            "clientes": clientes
        }
 
    def get_facturas(self):
        facturas = Factura.get_all()
        # clientes = Cliente.get_all()
        return {
            "facturas": facturas,
            # "clientes": clientes
        }

