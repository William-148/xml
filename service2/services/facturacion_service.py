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


class FacturacionService:

    def __init__(self):
        # Cargar datos base
        self.recursos = Recurso.get_dict_recursos()
        self.config_por_id = Categoria.get_dict_configuraciones()
        self.clientes = Cliente.get_all()

    def facturar(self, fecha_inicio: str, fecha_fin: str) -> List[Factura]:
        """
        Genera facturas para todos los clientes con consumos no facturados
        dentro del rango de fechas indicado.
        """
        fecha_ini = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        fecha_fn = datetime.strptime(fecha_fin, "%d/%m/%Y")

        grupos = GrupoConsumos.get_all()
        facturas: List[Factura] = []
        errors: List[str] = []

        for cliente in self.clientes:
            detalles: List[DetalleFactura] = []
            total_cliente = 0.0

            # Procesar todos los grupos de consumos asociados al cliente
            for grupo in grupos:
                if grupo.nitCliente.lower() != cliente.nit.lower():
                    continue

                # Filtrar consumos válidos
                consumos_validos = self._filtrar_consumos(grupo, fecha_ini, fecha_fn)
                if not consumos_validos:
                    continue

                horas = sum(c.tiempo for c in consumos_validos)
                id_conf = self._obtener_id_configuracion(cliente, grupo.idInstancia)
                if id_conf is None:
                    errors.append(f"Id de configuración no encontrado para el cliente '{cliente.nit}' y la instancia '{grupo.idInstancia}'.")
                    continue

                # Calcular costo de la instancia
                recursos_cantidad, subtotal = self._calcular_costo_instancia(id_conf, horas)
                total_cliente += subtotal

                # Marcar los consumos como facturados
                consumos_facturados = self._marcar_consumos_facturados(consumos_validos)

                detalles.append(
                    DetalleFactura(
                        idInstancia=grupo.idInstancia,
                        idConfiguracion=id_conf,
                        horas=horas,
                        subtotal=subtotal,
                        recursos_cantidad=recursos_cantidad,
                        consumos=consumos_facturados
                    )
                )

            if detalles:
                factura = Factura.generar(
                    nitCliente=cliente.nit,
                    rango_inicio=fecha_inicio,
                    rango_fin=fecha_fin,
                    detalles=detalles,
                    total=total_cliente
                )
                facturas.append(factura)
        if facturas:
            # Guardar las facturas en archivo XML
            Factura.write_xml(facturas)
            # Actualizar los consumos en el XML
            GrupoConsumos.write_xml(grupos)
        return {
            "facturas_generadas": len(facturas),
            "errors": errors
        }

    # ------------------------------
    # MÉTODOS AUXILIARES
    # ------------------------------
    def _filtrar_consumos(self, grupo: GrupoConsumos, fecha_ini: datetime, fecha_fin: datetime) -> List[Consumo]:
        """
        Devuelve los consumos no facturados dentro del rango de fechas.
        """
        consumos_validos = []
        for c in grupo.consumos:
            fecha = datetime.strptime(str(c.fechaHora), "%d/%m/%Y %H:%M")
            if fecha_ini <= fecha <= fecha_fin and not c.facturado:
                consumos_validos.append(c)
        return consumos_validos

    def _marcar_consumos_facturados(self, consumos: List[Consumo]) -> List[ConsumoFactura]:
        """
        Marca los consumos como facturados y retorna una nueva lista de consumos facturados.
        """
        consumos_facturados = []
        for c in consumos:
            c.facturado = True
            consumos_facturados.append(
                ConsumoFactura(
                    tiempo=c.tiempo,
                    fechaHora=str(c.fechaHora)
                )
            )
        return consumos_facturados

    def _obtener_id_configuracion(self, cliente: Cliente, id_instancia: int) -> int | None:
        """
        Retorna el idConfiguracion de la instancia especificada del cliente.
        """
        for inst in cliente.instancias:
            if inst.id == id_instancia:
                return inst.idConfiguracion
        return None

    def _calcular_costo_instancia(self, id_config: int, horas: float) -> Tuple[Dict[int, float], float]:
        """
        Calcula el costo total de una instancia dada su configuración y horas.
        """
        if id_config not in self.config_por_id:
            return 0.0
        configuracion = self.config_por_id[id_config]
        recursos_cantidad: Dict[int, float] = {}
        total = 0.0
        for rid, cantidad in configuracion.recursos.items():
            recurso = self.recursos.get(rid)
            if recurso:
                recursos_cantidad[rid] = cantidad
                total += cantidad * recurso.valorXhora * horas
        return recursos_cantidad, total

