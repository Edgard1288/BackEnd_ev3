from django.urls import path

from . import views

app_name = 'torneos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('gestion/', views.gestion, name='gestion'),
    path('gestion/crear/', views.crear, name='crear'),
    path('gestion/<int:id>/editar/', views.editar, name='editar'),
    path('gestion/<int:id>/eliminar/', views.eliminar, name='eliminar'),
    path('<slug:slug>/', views.detalle, name='detalle'),
]
