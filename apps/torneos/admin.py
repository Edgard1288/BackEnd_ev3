from django.contrib import admin

from .models import CategoriaJuego, Inscripcion, TorneoEvento


admin.site.register(CategoriaJuego)
admin.site.register(TorneoEvento)
admin.site.register(Inscripcion)
