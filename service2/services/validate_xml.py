from lxml import etree

def validate_xml(xml_string, xsd_path):
    try:
        with open(xsd_path, 'rb') as f:
            schema_doc = etree.XML(f.read())
            esquema = etree.XMLSchema(schema_doc)

        xml_doc = etree.fromstring(xml_string.encode('utf-8'))
        esquema.assertValid(xml_doc)
        return True, "XML válido según el esquema XSD."

    except etree.DocumentInvalid as e:
        return False, f"XML inválido: {str(e)}"
    except Exception as e:
        return False, f"Error al validar: {str(e)}"

