from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('consumo/', views.consumo, name='consumo'),
    path('inicializar_sistema/', views.inicializar_sistema, name='inicializar_sistema'),
    path('operaciones/', views.operaciones, name='operaciones'),
    path('recursos/', views.recursos, name='recursos'),
    path('categorias/', views.categorias, name='categorias'),
    path('clientes/', views.clientes, name='clientes'),
    path('facturas/', views.facturas, name='facturas'),
    path('facturacion/', views.facturacion, name='facturacion'),
    path('reportes/', views.reportes, name='reportes'),
]

