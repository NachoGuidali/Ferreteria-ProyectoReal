# def total_carrito(request):
#     total = 0
#     if request.user.is_authenticated:
#         if 'carrito' in request.session.keys():
#             for key, value in request.session['carrito'].items():
#                 total += int(value['subtotal'])
#     return {'total_carrito' : total}            

def total_carrito(request):
    total = 0
    carrito = request.session.get('carrito', {})  # Obtener el carrito de la sesión
    for key, value in carrito.items():
        total += int(value.get('subtotal', 0))  # Sumar los subtotales de cada elemento del carrito
    return {'total_carrito': total}
