from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TorneoEventoForm
from .models import CategoriaJuego, Inscripcion, TorneoEvento


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def lista(request):
    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '')
    orden = request.GET.get('orden', 'recientes')

    torneos = TorneoEvento.objects.filter(activo=True).select_related('categoria')
    if categoria_slug:
        torneos = torneos.filter(categoria__slug=categoria_slug)
    if query:
        torneos = torneos.filter(
            Q(nombre__icontains=query)
            | Q(organizador__icontains=query)
            | Q(reglas__icontains=query)
        )

    ordenes_validos = {
        'recientes': '-id',
        'precio_asc': 'costo_inscripcion',
        'precio_desc': '-costo_inscripcion',
    }
    torneos = torneos.order_by(ordenes_validos.get(orden, '-id'))
    pagina = Paginator(torneos, 9).get_page(request.GET.get('page'))

    return render(request, 'torneos/torneo_lista.html', {
        'torneos': pagina,
        'categorias': CategoriaJuego.objects.filter(activo=True),
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
    })


def detalle(request, slug):
    torneo = get_object_or_404(
        TorneoEvento.objects.select_related('categoria'),
        slug=slug,
        activo=True,
    )
    inscrito = request.user.is_authenticated and torneo.inscripciones.filter(
        usuario=request.user,
    ).exists()
    carrito = request.session.get("carrito_torneos", [])
    return render(request, 'torneos/torneo_detalle.html', {
        'torneo': torneo,
        'inscrito': inscrito,
        'en_carrito': isinstance(carrito, list) and torneo.pk in carrito,
    })


@login_required
@require_POST
def cancelar_inscripcion(request, slug):
    inscripcion = get_object_or_404(
        Inscripcion.objects.select_related("torneo"),
        torneo__slug=slug,
        usuario=request.user,
    )
    if inscripcion.torneo.estado != "abierto":
        messages.error(
            request,
            "Solo puedes cancelar tu inscripción antes de que comience el torneo.",
        )
    else:
        nombre_torneo = inscripcion.torneo.nombre
        inscripcion.delete()
        messages.success(request, f"Cancelaste tu inscripción en '{nombre_torneo}'.")
    return redirect("usuarios:perfil")


@login_required
@user_passes_test(es_administrador, login_url='torneos:lista')
def gestion(request):
    torneos = TorneoEvento.objects.select_related('categoria').order_by('-id')
    return render(request, 'torneos/gestion_torneos.html', {'torneos': torneos})


@login_required
@user_passes_test(es_administrador, login_url='torneos:lista')
def crear(request):
    form = TorneoEventoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        torneo = form.save()
        messages.success(request, f"Torneo '{torneo.nombre}' creado exitosamente.")
        return redirect('torneos:gestion')
    return render(request, 'torneos/torneo_form.html', {
        'form': form,
        'titulo_accion': 'Crear Torneo',
        'boton_texto': 'Guardar',
    })


@login_required
@user_passes_test(es_administrador, login_url='torneos:lista')
def editar(request, id):
    torneo = get_object_or_404(TorneoEvento, id=id)
    form = TorneoEventoForm(request.POST or None, request.FILES or None, instance=torneo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Torneo '{torneo.nombre}' actualizado.")
        return redirect('torneos:gestion')
    return render(request, 'torneos/torneo_form.html', {
        'form': form,
        'torneo': torneo,
        'titulo_accion': 'Editar Torneo',
        'boton_texto': 'Actualizar',
    })


@login_required
@user_passes_test(es_administrador, login_url='torneos:lista')
def eliminar(request, id):
    torneo = get_object_or_404(TorneoEvento, id=id)
    if request.method == 'POST':
        nombre = torneo.nombre
        torneo.delete()
        messages.success(request, f"Torneo '{nombre}' eliminado.")
        return redirect('torneos:gestion')
    return render(request, 'torneos/torneo_confirmar_eliminar.html', {'torneo': torneo})
