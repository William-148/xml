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
from models.classes.configuracion import Configuracion


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
        return { "recursos": Recurso.get_all() }

    def get_categorias(self):
        recursos = Recurso.get_dict_recursos()
        categorias = Categoria.get_all()
        categorias_dict = []

        def procesar_configuracion(config: Configuracion) -> Dict:
            config_dict = config.to_dict()
            config_dict["recursos"] = []
            for recurso_id, cantidad in config.recursos.items():
                rec_found = recursos.get(recurso_id)
                if rec_found is None:
                    continue
                rec_dict = rec_found.to_dict()
                rec_dict["cantidad"] = cantidad
                config_dict["recursos"].append(rec_dict)
            return config_dict

        for categoria in categorias:
            categoria_dict = categoria.to_dict(incluir_configuraciones=False)
            for configuracion in categoria.configuraciones:
                config_dict = procesar_configuracion(configuracion)
                categoria_dict.setdefault("configuraciones", []).append(config_dict)
            categorias_dict.append(categoria_dict)

        return {
            "categorias": categorias_dict,
        }


    def get_clientes(self):
        recursos = Recurso.get_dict_recursos()
        config_por_id = Categoria.get_dict_configuraciones()
        clientes = Cliente.get_all()
        grupo_consumos = GrupoConsumos.get_all_dict()
        clientes_dict = []

        def crear_configuracion(id_configuracion: int) -> Dict:
            config = config_por_id.get(id_configuracion)
            config_dict = config.to_dict()
            config_dict["recursos"] = []
            for recurso_id, cantidad in config.recursos.items():
                rec_found = recursos.get(recurso_id)
                if rec_found is None:
                    continue
                rec_dict = rec_found.to_dict()
                rec_dict["cantidad"] = cantidad
                config_dict["recursos"].append(rec_dict)
            return config_dict

        for cliente in clientes:
            cliente_dict = cliente.to_dict()
            for instancia in cliente.instancias:
                instancia_dict = instancia.to_dict()
                # Generando configuracion de instancia
                config_found = config_por_id.get(instancia.idConfiguracion)
                instancia_dict["configuracion"] = crear_configuracion(instancia.idConfiguracion)
                # Generando consumos de instancia
                g_consumo_found = grupo_consumos.get(f"{cliente.nit.lower()}-{str(instancia.id)}")
                if g_consumo_found is not None:
                    instancia_dict["consumos"] = [c.to_dict() for c in g_consumo_found.consumos]
                # Agregando instancia al cliente
                cliente_dict.setdefault("instancias", []).append(instancia_dict)
            clientes_dict.append(cliente_dict)

        return {
            "clientes": clientes_dict,
        }
 
    def get_facturas(self):
        recursos = Recurso.get_dict_recursos()
        facturas = Factura.get_all()
        clientes = Cliente.get_all_dict()
        facturas_dict = []

        def procesar_detalle_factura(detalle:DetalleFactura) -> Dict:
            detalle_dict = detalle.to_dict()
            detalle_dict["recursos"] = []
            for recurso_id, cantidad in detalle.recursos_cantidad.items():
                rec_found = recursos.get(recurso_id)
                if rec_found is None:
                    continue
                rec_dict = rec_found.to_dict()
                rec_dict["cantidad"] = cantidad
                detalle_dict["recursos"].append(rec_dict)
            return detalle_dict


        for factura in facturas:
            factura_dict = factura.to_dict(incluir_detalles=False)
            cliente_found = clientes.get(factura.nitCliente)
            if cliente_found is None:
                continue

            factura_dict["cliente"] = cliente_found.to_dict()
            for detalle in factura.detalles:
                detalle_dict = procesar_detalle_factura(detalle)
                # Encontrar instancia asociada
                for instancia in cliente_found.instancias:
                    if instancia.id == detalle.idInstancia:
                        detalle_dict["instancia"] = instancia.to_dict()
                        break
                # Agregar detalle a la factura
                factura_dict.setdefault("detalles", []).append(detalle_dict)

            facturas_dict.append(factura_dict)


        return {
            "facturas": facturas_dict
        }

