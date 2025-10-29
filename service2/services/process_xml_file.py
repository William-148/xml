import xml.etree.ElementTree as ET
from models.classes.recurso import Recurso
from models.classes.categoria import Categoria
from models.classes.cliente import Cliente
from models.exceptions import ValidationError
from models.classes.consumo import Consumo, GrupoConsumos

def procesar_configuracion(xml_string):
    root = ET.fromstring(xml_string)
    errors = []
 
    # Procesando recursos
    resources = []
    resource_list = root.find('listaRecursos')
    if resource_list is not None:
        for nodo in resource_list.findall('recurso'):
            try:
                resource = Recurso.from_element(nodo)
                resources.append(resource)
            except ValidationError as e:
                errors.append(f"Error al procesar recurso: {e}")

    # Procesando categorias
    categories = []
    countConfigurations = 0
    category_list = root.find('listaCategorias')
    if category_list is not None:
        for nodo in category_list.findall('categoria'):
            try:
                category = Categoria.from_element(nodo)
                categories.append(category)
                countConfigurations += len(category.configuraciones)
            except ValidationError as e:
                errors.append(f"Error al procesar categoria: {e}")

    # Procesando clientes
    clients = []
    countInstances = 0
    client_list = root.find('listaClientes')
    if client_list is not None:
        for nodo in client_list.findall('cliente'):
            try:
                client, c_errors = Cliente.from_element(nodo)
                clients.append(client)
                countInstances += len(client.instancias)
                if c_errors is not None:
                    errors.append(f"Errores en cliente {client.nit}: {c_errors}")
            except ValidationError as e:
                errors.append(f"Error al procesar cliente: {e}")

    # Creando archivos XML
    if len(resources) > 0: Recurso.write_xml(resources)
    if len(categories) > 0: Categoria.write_xml(categories)
    if len(clients) > 0: Cliente.write_xml(clients)

    return {
        "recursos_creados": len(resources),
        "categorias_creadas": len(categories),
        "configuraciones_creadas": countConfigurations,
        "clientes_creados": len(clients),
        "instancias_creadas": countInstances,
        "errors": errors
    }

def procesar_consumo(xml_string):
    root = ET.fromstring(xml_string)
    errors = []

    # Procesando consumos
    grupos: Dict[Tuple[str, int], GrupoConsumo] = {}
    countConsumptions = 0
    consumption_list = root
    if consumption_list is not None:
        for nodo in consumption_list.findall('consumo'):
            try:
                nitCliente = nodo.attrib["nitCliente"]
                idInstancia = int(nodo.attrib["idInstancia"])
                clave = (nitCliente, idInstancia)
                if clave not in grupos:
                    grupos[clave] = GrupoConsumos(nitCliente = nitCliente, idInstancia = idInstancia)
                grupos[clave].consumos.append(
                    Consumo(
                        tiempo = float(nodo.findtext("tiempo", "0")),
                        fechaHora = nodo.findtext("fechaHora", ""),
                    )
                )
                countConsumptions += 1

            except ValidationError as e:
                errors.append(f"Error al procesar consumo: {e}")
    if len(grupos) > 0:
        # GrupoConsumos.write_xml(list(grupos.values()))
        GrupoConsumos.append_xml(list(grupos.values()))


    return {
        "consumos_procesados": countConsumptions,
        "errors": errors
    }

