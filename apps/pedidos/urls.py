from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('carrito/', views.carrito_ver, name='ver'),
    path('carrito/agregar-torneo/<slug:slug>/', views.carrito_agregar_torneo, name='agregar_torneo'),
    path('carrito/quitar-torneo/<slug:slug>/', views.carrito_quitar_torneo, name='quitar_torneo'),
    path('carrito/confirmar/', views.carrito_confirmar, name='confirmar'),
]