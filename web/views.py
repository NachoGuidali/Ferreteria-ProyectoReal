import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from urllib.parse import quote
from .models import Producto
from .Carrito import Carrito
from .context_processors import total_carrito

from .forms import CargarProductosForm


# Create your views here.

def home(request):
    context = {}
    return render(request, 'home.html', context)


def lista_productos(request):
    productos = Producto.objects.all()

    keyword_name = request.GET.get('name')
    keyword_proveedor = request.GET.get('proveedor')
    if keyword_name:
        productos = productos.filter(nombre__icontains=keyword_name)
    else:
        keyword_name = ""
    if keyword_proveedor:
        productos = productos.filter(proveedor__icontains=keyword_proveedor)
    else:
        keyword_proveedor = ''    
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'lista_productos.html', {'page_obj': page_obj, 'keyword_name': keyword_name, 'keyword_proveedor': keyword_proveedor})

@login_required
def cargar_productos(request):
    if request.method == 'POST':
        form = CargarProductosForm(request.POST, request.FILES)
        if form.is_valid():
            Producto.objects.all().delete()
            archivo_excel = request.FILES['archivo_excel']
            try:
                df = pd.read_excel(archivo_excel)
                for index, row in df.iterrows():
                    Producto.objects.create(
                        codigo=row['codigo'],
                        nombre=row['nombre'],
                        proveedor=row['proveedor'],
                        precio=row['precio'],
                    )
                return redirect('productos')
            except Exception as e:
                return render (request, 'cargar_productos.html', {'form': form, 'error_message':str(e)}) 
    else:
        form = CargarProductosForm()
    return render(request, 'cargar_productos.html', {'form': form})               


def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = Carrito(request)
        producto = Producto.objects.get(id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario, o establecerla en 1 por defecto
        carrito.agregar(producto, cantidad)
    return redirect('productos')

def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    return redirect('carrito')

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    return redirect('carrito')

def vaciar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect('productos')

"""def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))  # Si no se proporciona ninguna cantidad, establecerla en 1 por defecto
    carrito = request.session.get('carrito', {})
    print(type(cantidad))
    if producto_id in carrito:
        carrito[producto_id] += cantidad  # Incrementar la cantidad existente
        print(type(cantidad))
    else:
        carrito[producto_id] = cantidad  # Almacenar la cantidad para un nuevo producto
    
    request.session['carrito'] = carrito
    request.session.modified = True  # Marcar la sesión como modificada para asegurar que se guarde correctamente
    print(type(cantidad))
    return redirect('productos')



def eliminar_del_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        if producto_id in carrito:
            del carrito[producto_id]
            request.session['carrito'] = carrito
    return redirect('ver_carrito')"""




# def enviar_carrito_por_whatsapp(request):
#     carrito = request.session.get('carrito', {})
#     # Generar mensaje con los detalles del carrito
#     mensaje = "Mi carrito de compras:\n"
#     for producto_id, cantidad in carrito.items():
#         producto = Producto.objects.get(id=producto_id)
#         mensaje += f"{producto.nombre} - Cantidad: {cantidad}\n"
    
#     # Redirigir a Whatsapp con el mensaje prellenado
#     url_whatsapp = f"https://api.whatsapp.com/send?phone=1163589975&text={mensaje}"
#     return redirect(url_whatsapp)


# def vaciar_carrito(request):
#     if request.method == 'POST':
#         request.session['carrito'] = {}
#     return redirect('ver_carrito')



# def ver_carrito(request):
#     carrito = request.session.get('carrito', {})
#     productos_en_carrito = []
#     total_carrito = 0
#     cantidad = type(int)
#     for producto_id, cantidad in carrito.items():
#         producto = get_object_or_404(Producto, pk=producto_id)
#         subtotal = producto.precio * cantidad
#         total_carrito += subtotal
#         productos_en_carrito.append({
#             'producto': producto,
#             'cantidad': cantidad,
#             'subtotal': subtotal
#         })
    
#     return render(request, 'carrito.html', {
#      'productos_en_carrito': productos_en_carrito,
#         'total_carrito': total_carrito
#     })

def ver_carrito(request):
    carrito = Carrito(request)  # Inicializa la instancia de la clase Carrito con la solicitud actual
    carrito.calcular_subtotales()  # Calcula los subtotales para cada elemento del carrito
    contenido_carrito = carrito.carrito  # Obtén el contenido del carrito desde la instancia de la clase Carrito

    # Puedes pasar el contenido del carrito a la plantilla para renderizarlo
    return render(request, 'carrito.html', {'contenido_carrito': contenido_carrito})

def enviar_carrito_por_whatsapp(request):
    carrito = Carrito(request)
    contenido_carrito = carrito.carrito

    mensaje = "¡Hola! Quisiera realizar el siguiente pedido:\n\n"
    total_carrito_msj = total_carrito(request)['total_carrito']
    for item in contenido_carrito.values():
        mensaje += f"Cod: {item['codigo']} - {item['nombre']} - Cantidad: {item['cantidad']} - Subtotal: ${item['subtotal']}\n"

    mensaje += f"\n*Total del pedido: ${total_carrito_msj}*"

    # Número de teléfono al que se enviará el mensaje (debe estar en el formato internacional)
    numero_destino = '5491130125525'  # Reemplazar con el número del dueño del local

    # Codificar el mensaje para que sea una URL válida
    mensaje_codificado = quote(mensaje)

    # Construir el enlace de WhatsApp con el mensaje y el número de destino
    enlace_whatsapp = f"https://api.whatsapp.com/send?phone={numero_destino}&text={mensaje_codificado}"

    # Redirigir al usuario al enlace de WhatsApp
    return redirect(enlace_whatsapp)