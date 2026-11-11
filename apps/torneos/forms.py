from django import forms

from .models import TorneoEvento


class TorneoEventoForm(forms.ModelForm):
    class Meta:
        model = TorneoEvento
        fields = (
            'nombre',
            'categoria',
            'organizador',
            'reglas',
            'costo_inscripcion',
            'cupos_maximos',
            'banner',
            'estado',
            'activo',
        )
