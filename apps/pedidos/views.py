from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.torneos.models import Inscripcion, TorneoEvento
from .models import ComprobanteInscripcion, DetalleComprobante, formato_clp
from .pricing import calcular_desglose


CARRITO_TORNEOS = "carrito_torneos"


def _ids_carrito(request):
    ids = request.session.get(CARRITO_TORNEOS, [])
    if not isinstance(ids, list):
        return []
    return list(dict.fromkeys(item for item in ids if isinstance(item, int)))


def carrito_ver(request):
    ids = _ids_carrito(request)
    torneos = TorneoEvento.objects.filter(
        pk__in=ids,
        activo=True,
    ).select_related("categoria")
    torneos_por_id = {torneo.pk: torneo for torneo in torneos}
    items = [torneos_por_id[torneo_id] for torneo_id in ids if torneo_id in torneos_por_id]

    if len(items) != len(ids):
        request.session[CARRITO_TORNEOS] = [torneo.pk for torneo in items]
        messages.warning(request, "Se quitaron del carrito torneos que ya no están disponibles.")

    subtotal = sum((torneo.costo_inscripcion for torneo in items), start=0)
    desglose = calcular_desglose(subtotal)
    return render(request, "pedidos/carrito.html", {
        "torneos": items,
        **desglose,
        "subtotal_formateado": formato_clp(desglose["subtotal"]),
        "subtotal_neto_formateado": formato_clp(desglose["subtotal_neto"]),
        "recargo_servicio_formateado": formato_clp(desglose["recargo_servicio"]),
        "iva_formateado": formato_clp(desglose["iva"]),
        "total_formateado": formato_clp(desglose["total"]),
    })


@require_POST
def carrito_agregar_torneo(request, slug):
    torneo = get_object_or_404(TorneoEvento, slug=slug, activo=True)
    if torneo.estado != "abierto" or torneo.cupos_disponibles <= 0:
        messages.error(request, "Este torneo ya no tiene cupos disponibles para inscripción.")
    elif request.user.is_authenticated and Inscripcion.objects.filter(
        torneo=torneo,
        usuario=request.user,
    ).exists():
        messages.info(request, "Ya estás inscrito en este torneo.")
    else:
        ids = _ids_carrito(request)
        if torneo.pk not in ids:
            ids.append(torneo.pk)
            request.session[CARRITO_TORNEOS] = ids
            messages.success(request, f"'{torneo.nombre}' se agregó a tu carrito.")
        else:
            messages.info(request, "Este torneo ya está en tu carrito.")

    return redirect("pedidos:ver")


@require_POST
def carrito_quitar_torneo(request, slug):
    torneo = get_object_or_404(TorneoEvento, slug=slug)
    ids = _ids_carrito(request)
    request.session[CARRITO_TORNEOS] = [torneo_id for torneo_id in ids if torneo_id != torneo.pk]
    return redirect("pedidos:ver")


@require_POST
@login_required
def carrito_confirmar(request):
    ids = _ids_carrito(request)
    if not ids:
        messages.info(request, "Tu carrito no tiene torneos para confirmar.")
        return redirect("pedidos:ver")

    with transaction.atomic():
        torneos = list(
            TorneoEvento.objects.select_for_update()
            .filter(pk__in=ids, activo=True)
            .order_by("pk")
        )
        torneos_por_id = {torneo.pk: torneo for torneo in torneos}
        if len(torneos) != len(ids):
            messages.error(request, "Hay torneos de tu carrito que ya no están disponibles.")
            return redirect("pedidos:ver")

        for torneo_id in ids:
            torneo = torneos_por_id[torneo_id]
            if Inscripcion.objects.filter(torneo=torneo, usuario=request.user).exists():
                messages.error(request, f"Ya estás inscrito en '{torneo.nombre}'.")
                return redirect("pedidos:ver")
            if torneo.estado != "abierto":
                messages.error(request, f"'{torneo.nombre}' ya no está abierto para inscripciones.")
                return redirect("pedidos:ver")
            if torneo.cupos_disponibles <= 0:
                messages.error(request, f"'{torneo.nombre}' ya no tiene cupos disponibles.")
                return redirect("pedidos:ver")

        subtotal = sum((torneo.costo_inscripcion for torneo in torneos), start=0)
        desglose = calcular_desglose(subtotal)
        comprobante = ComprobanteInscripcion.objects.create(
            usuario=request.user,
            subtotal=desglose["subtotal"],
            subtotal_neto=desglose["subtotal_neto"],
            recargo_servicio=desglose["recargo_servicio"],
            iva=desglose["iva"],
            total=desglose["total"],
            iva_incluido=True,
        )
        DetalleComprobante.objects.bulk_create([
            DetalleComprobante(
                comprobante=comprobante,
                torneo=torneo,
                nombre_torneo=torneo.nombre,
                categoria_torneo=torneo.categoria.nombre,
                precio_inscripcion=torneo.costo_inscripcion,
            )
            for torneo in torneos
        ])
        Inscripcion.objects.bulk_create([
            Inscripcion(torneo=torneo, usuario=request.user)
            for torneo in torneos
        ])

    del request.session[CARRITO_TORNEOS]
    messages.success(request, "Tu inscripción quedó confirmada correctamente.")
    return redirect("pedidos:comprobante", codigo=comprobante.codigo)


@login_required
def comprobante_ver(request, codigo):
    comprobante = get_object_or_404(
        ComprobanteInscripcion.objects.prefetch_related("detalles"),
        codigo=codigo,
        usuario=request.user,
    )
    return render(request, "pedidos/comprobante.html", {
        "comprobante": comprobante,
    })
