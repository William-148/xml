from flask import Flask, request, jsonify, send_file
from services.validate_xml import validate_xml
from services.process_xml_file import procesar_configuracion, procesar_consumo
from services.facturacion_service import FacturacionService
from services.factura_pdf_service import FacturaPdfService
from services.state_service import StateService
from services.reporte_service import ReporteService
from models.classes.recurso import Recurso
from models.classes.categoria import Categoria

import os
import glob


app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Backend está activo."})

@app.route('/datos')
def state():
    try:
        state_service = StateService()
        # Procesar
        result = state_service.get_app_state()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/recursos')
def get_recursos():
    try:
        state_service = StateService()
        # Procesar
        result = state_service.get_recursos()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/recursos', methods=['POST'])
def create_recursos():
    try:
        data = request.get_json()
        Recurso.add_recurso(
            data.get("nombre"),
            data.get("abreviatura"),
            data.get("metrica"),
            data.get("tipo"),
            float(data.get("valorXhora"))
        )
        return jsonify({"message": "Creado con éxito."}), 200

    except Exception as e:
        return jsonify({"error": f"Error al crear recurso: {str(e)}"}), 500

@app.route('/categorias')
def get_categorias():
    try:
        state_service = StateService()
        # Procesar
        result = state_service.get_categorias()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/categorias', methods=['POST'])
def create_categoria():
    try:
        data = request.get_json()
        Categoria.add_categoria(
            data.get("nombre"),
            data.get("descripcion"),
            data.get("cargaTrabajo"),
        )
        return jsonify({"message": "Creado con éxito."}), 200

    except Exception as e:
        return jsonify({"error": f"Error al crear recurso: {str(e)}"}), 500

@app.route('/clientes')
def get_clientes():
    try:
        state_service = StateService()
        # Procesar
        result = state_service.get_clientes()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/clientes', methods=['POST'])
def create_cliente():
    try:
        data = request.get_json()
        from models.classes.cliente import Cliente
        Cliente.add_cliente(
            data.get("nit"),
            data.get("nombre"),
            data.get("direccion"),
            data.get("correoElectronico")
        )
        return jsonify({"message": "Cliente creado con éxito."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al crear cliente: {str(e)}"}), 500


@app.route('/facturas')
def get_facturas():
    try:
        state_service = StateService()
        # Procesar
        result = state_service.get_facturas()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/crear_configuracion', methods=['POST'])
def crear_configuracion():
    archivo = request.files.get('archivo')
    if not archivo:
        return jsonify({"error": "No se recibió ningún archivo"}), 400

    try:
        # Obtener el contenido del archivo XML
        xml_content = archivo.read().decode('utf-8')
        # Cargar y validar el XML contra el esquema XSD
        isValid, message = validate_xml(xml_content, 'schemas/configuracion.xsd')
        if not isValid:
            return jsonify({"error": message }), 400

        # Procesar
        result = procesar_configuracion(xml_content)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500


@app.route('/consumo', methods=['POST'])
def consumo():
    archivo = request.files.get('archivo')
    if not archivo:
        return jsonify({"error": "No se recibió ningún archivo"}), 400

    try:
        # Obtener el contenido del archivo XML
        xml_content = archivo.read().decode('utf-8')
        # Cargar y validar el XML contra el esquema XSD
        isValid, message = validate_xml(xml_content, 'schemas/consumo.xsd')
        if not isValid:
            return jsonify({"error": message }), 400

        # Procesar
        result = procesar_consumo(xml_content)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/limpiar-db', methods=['POST'])
def limpiar_xml():
    try:
        print('hola mudo')
        archivos = glob.glob(os.path.join("data", '*.xml'))
        eliminados = []
        print(archivos)

        for archivo in archivos:
            os.remove(archivo)
            eliminados.append(os.path.basename(archivo))


        return jsonify({
            'mensaje': 'Archivos XML eliminados correctamente.',
            'archivos_eliminados': eliminados
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/facturas/<factura_id>")
def generar_pdf_factura(factura_id: str):
    try:
        service = FacturaPdfService(int(factura_id))
        ruta_pdf = service.generar_pdf()
        return send_file(ruta_pdf, mimetype="application/pdf", as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Error al generar pdf: {str(e)}"}), 500

@app.route('/factura', methods=['POST'])
def generar_facturas():
    data = request.get_json()

    fecha_inicio_str = data.get("fecha_inicio")
    fecha_fin_str = data.get("fecha_fin")

    if not fecha_inicio_str or not fecha_fin_str:
        return jsonify({"error": "Rango de fecha no provisto."}), 400

    try:
        facturacion_service = FacturacionService()
        result = facturacion_service.facturar(fecha_inicio_str, fecha_fin_str)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Error al generar facturas: {str(e)}"}), 500

@app.route("/reporte/<reporte_id>", methods=['POST'])
def generar_reporte_pdf(reporte_id: str):
    data = request.get_json()

    fecha_inicio_str = data.get("fecha_inicio")
    fecha_fin_str = data.get("fecha_fin")

    if not fecha_inicio_str or not fecha_fin_str:
        return jsonify({"error": "Rango de fecha no provisto."}), 400

    try:
        reporte_service = ReporteService(fecha_inicio_str, fecha_fin_str)
        ruta_pdf = ""
        if reporte_id == "1":
            ruta_pdf = reporte_service.reporte1()
        elif reporte_id == "2":
            ruta_pdf = reporte_service.reporte2()
        else:
            return jsonify({"error": f"ID de reporte no válido '{reporte_id}'."}), 400
        return send_file(ruta_pdf, mimetype="application/pdf", as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Error al generar reporte: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

