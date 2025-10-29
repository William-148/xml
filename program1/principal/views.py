from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib import messages
from .services.configuration_service import enviar_configuracion, enviar_consumo
from django.conf import settings
import requests

# Create your views here.
def index(request):
    return render(request, 'principal/index.html')

def configuracion(request):
    resultado = None
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        response = enviar_configuracion(archivo)
        print(response, response.status_code )
        if response and response.status_code == 200:
            resultado = response.json()
            messages.success(request, 'Archivo enviado exitosamente.')
        elif response is not None and response.status_code == 400:
            resultado = response.json()
            messages.error(request, f'Error en el archivo enviado.')
        elif response is not None:
            messages.error(request, f'Error al enviar el archivo: {response.status_code}')
        else:
            messages.error(request, 'No se pudo conectar con la API.')
    return render(request, 'principal/configuracion.html', {'resultado': resultado})

def consumo(request):
    resultado = None
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        response = enviar_consumo(archivo)
        print(response, response.status_code )
        if response and response.status_code == 200:
            resultado = response.json()
            messages.success(request, 'Archivo enviado exitosamente.')
        elif response is not None and response.status_code == 400:
            resultado = response.json()
            messages.error(request, f'Error en el archivo enviado.')
        elif response is not None:
            messages.error(request, f'Error al enviar el archivo: {response.status_code}')
        else:
            messages.error(request, 'No se pudo conectar con la API.')

    return render(request, 'principal/consumo.html', {'resultado': resultado})

def operaciones(request):
    return render(request, 'principal/operaciones.html')

def inicializar_sistema(request):
    try:
        response = requests.post(f"{settings.API_HOST}/limpiar-db")
        datos = response.json() if response.status_code == 200 else {}
        messages.success(request, 'Base de datos inicializada correctamente.')
    except requests.exceptions.RequestException:
        datos = {}
        messages.error(request, 'Error al inicializar la base de datos.')
    return render(request, 'principal/operaciones.html')


def recursos(request):
    try:
        response = requests.get(f"{settings.API_HOST}/recursos")
        datos = response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        datos = {}
    return render(request, 'principal/recursos.html', {'datos': datos})

def categorias(request):
    try:
        response = requests.get(f"{settings.API_HOST}/categorias")
        datos = response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        datos = {}
    return render(request, 'principal/categorias.html', {'datos': datos})

def clientes(request):
    try:
        response = requests.get(f"{settings.API_HOST}/clientes")
        datos = response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        datos = {}
    return render(request, 'principal/clientes.html', {'datos': datos})

def facturas(request):
    try:
        response = requests.get(f"{settings.API_HOST}/facturas")
        datos = response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        datos = {}
    return render(request, 'principal/facturas.html', {'datos': datos, 'factura_endpoint': f"{settings.API_HOST}/facturas" })

@csrf_exempt
def facturacion(request):
    if request.method == 'POST':
        fecha_inicio_raw = request.POST.get('fecha_inicio')
        fecha_fin_raw = request.POST.get('fecha_fin')

        # Convertir a objeto datetime
        fecha_inicio_obj = datetime.strptime(fecha_inicio_raw, '%Y-%m-%d')
        fecha_fin_obj = datetime.strptime(fecha_fin_raw, '%Y-%m-%d')

        fecha_inicio = fecha_inicio_obj.strftime('%d/%m/%Y')
        fecha_fin = fecha_fin_obj.strftime('%d/%m/%Y')
        # Aquí haces la lógica para generar las facturas
        try:
            response = requests.post(
                f"{settings.API_HOST}/factura",
                json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin}
            )
            if response.status_code == 200:
                datos = response.json()
                messages.success(request, 'Facturacion realizada correctamente.')
            else:
                datos = response.json()
                print(response.status_code)
                print(datos)
                messages.error(request, f'No se pudo realizar la operación. {datos}')

        except requests.exceptions.RequestException:
            datos = {}
            messages.error(request, 'Error al realizar la facturacion.')

        return render(request, 'principal/operaciones.html', {"resultado": datos})
    return redirect('operaciones')

def reportes(request):
    return render(request, 'principal/reportes.html')

