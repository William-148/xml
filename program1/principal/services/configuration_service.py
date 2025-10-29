import requests
from django.conf import settings

def enviar_configuracion(ruta_archivo):
    url = f"{settings.API_HOST}/crear_configuracion"
    files = {
        'archivo': (ruta_archivo.name, ruta_archivo.file, 'application/xml')
    }
    try:
        response = requests.post(url, files=files)
        return response
    except requests.exceptions.RequestException as e:
        return None, str(e)

def enviar_consumo(ruta_archivo):
    url = f"{settings.API_HOST}/consumo"
    files = {
        'archivo': (ruta_archivo.name, ruta_archivo.file, 'application/xml')
    }
    try:
        response = requests.post(url, files=files)
        return response
    except requests.exceptions.RequestException as e:
        return None, str(e)

