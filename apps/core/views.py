from django.shortcuts import render
from apps.torneos.models import TorneoEvento, CategoriaJuego

def inicio(request):
    destacados = TorneoEvento.objects.filter(activo=True, estado='abierto')[:4]
    categorias = CategoriaJuego.objects.filter(activo=True)
    return render(request, 'core/index.html', {
        'destacados': destacados,
        'categorias': categorias,
    })

def nosotros(request):
    return render(request, 'core/nosotros.html')