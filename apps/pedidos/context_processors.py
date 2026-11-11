def carrito_context(request):
    carrito = request.session.get('carrito_torneos', [])
    return {
        'carrito_total_items': len(carrito) if isinstance(carrito, list) else 0,
    }