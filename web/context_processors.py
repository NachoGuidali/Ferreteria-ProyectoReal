# def total_carrito(request):
#     total = 0
#     if request.user.is_authenticated:
#         if 'carrito' in request.session.keys():
#             for key, value in request.session['carrito'].items():
#                 total += int(value['subtotal'])
#     return {'total_carrito' : total}            

# def total_carrito(request):
#     total = 0
#     carrito = request.session.get('carrito', {})  # Obtener el carrito de la sesión
#     for key, value in carrito.items():
#         total += round(value.get('subtotal', 0), 2)  # Sumar los subtotales de cada elemento del carrito
#     return {'total_carrito': total}



def total_carrito(request):
    total_usd = 0
    total_pesos = 0
    carrito = request.session.get('carrito', {})  # Obtener el carrito de la sesión
    for key, value in carrito.items():
        subtotal = value.get('subtotal', 0)
        if value.get('tipo_moneda') == 'DOLARIZADO':
            total_usd += subtotal
        else:
            total_pesos += subtotal
    return {'total_carrito_usd': round(total_usd, 2), 'total_carrito_pesos': round(total_pesos, 2)}
