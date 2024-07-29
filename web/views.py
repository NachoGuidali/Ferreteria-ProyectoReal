import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from urllib.parse import quote
from .models import Producto
from .Carrito import Carrito
from .context_processors import total_carrito

from .forms import CargarProductosForm

from .tasks import procesar_archivo_excel
from django.conf import settings
import os



# Create your views here.

def home(request):
    context = {}
    return render(request, 'home.html', context)


def lista_productos(request):
    productos = Producto.objects.all()
  
    # LOGICA DEL BUSCADOR 
    keyword_name = request.GET.get('name')
    keyword_proveedor = request.GET.get('proveedor')
    keyword_codigo = request.GET.get('codigo')

    """if keyword_name:
        productos = productos.filter(nombre__icontains=keyword_name)"""
    if keyword_name:
        keyword_name = keyword_name.split()
        query_name = Q()
        for word in keyword_name:
            query_name &= Q(nombre__icontains=word)
        productos = productos.filter(query_name)    
    else:
        keyword_name = ""
    if keyword_codigo:
        productos = productos.filter(codigo__icontains=keyword_codigo)
    else:
        keyword_codigo = ""     
    if keyword_proveedor:
        productos = productos.filter(proveedor__icontains=keyword_proveedor)
    else:
        keyword_proveedor = ''    

    # PAGINADOR
    paginator = Paginator(productos, 15)
    page_number = request.GET.get('page')
       
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    for producto in page_obj:
        if producto.tipo_moneda == 'DOLARIZADO':
            producto.precio_con_moneda = f"USD {round(producto.precio, 2)}"   
        else:
            producto.precio_con_moneda = f"$ {round(producto.precio, 2)}"

    # Calcular los rangos de páginas a mostrar
    total_pages = paginator.num_pages
    current_page = page_obj.number
    max_pages_shown = 9
    half_max_pages_shown = max_pages_shown // 2

    start_page = max(current_page - half_max_pages_shown, 1)
    end_page = min(current_page + half_max_pages_shown, total_pages)

    if end_page - start_page < max_pages_shown:
        if start_page == 1:
            end_page = min(start_page + max_pages_shown - 1, total_pages)
        else:
            start_page = max(end_page - max_pages_shown + 1, 1)

    page_range = range(start_page, end_page + 1)

    return render(request, 'lista_productos.html', {'page_obj': page_obj, 'keyword_name': keyword_name, 'keyword_proveedor': keyword_proveedor, 'page_range': page_range})

@login_required
def cargar_productos(request):
    if request.method == 'POST':
        form = CargarProductosForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            # Guardar el archivo en el sistema de archivos
            ruta_archivo = os.path.join(settings.MEDIA_ROOT, archivo_excel.name)
            with open(ruta_archivo, 'wb') as f:
                for chunk in archivo_excel.chunks():
                    f.write(chunk)
            # Llamar a la tarea Celery con la ruta del archivo
            procesar_archivo_excel.delay(ruta_archivo)
            return redirect('productos')
    else:
        form = CargarProductosForm()
    return render(request, 'cargar_productos.html', {'form': form})
# def cargar_productos(request):
#     if request.method == 'POST':
#         form = CargarProductosForm(request.POST, request.FILES)
#         if form.is_valid():
#             Producto.objects.all().delete()
#             archivo_excel = request.FILES['archivo_excel']
#             try:
#                 df = pd.read_excel(archivo_excel, skiprows=8)
#                 for index, row in df.iterrows():
#                     Producto.objects.create(
#                         codigo=row['Codigo'],
#                         nombre=row['Producto'],
#                         proveedor=row['Marca'],
#                         tipo_moneda=row['TipoMoneda'],
#                         precio=row['Precio'],
#                     )
#                 return redirect('productos')
#             except Exception as e:
#                 return render (request, 'cargar_productos.html', {'form': form, 'error_message':str(e)}) 
#     else:
#         form = CargarProductosForm()
#     return render(request, 'cargar_productos.html', {'form': form})           


@csrf_exempt
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = Carrito(request)
        producto = Producto.objects.get(id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        carrito.agregar(producto, cantidad)
        return JsonResponse({'message': 'Agregado al carrito correctamente.'})
    else:
        return JsonResponse({'message': 'Error al agregar al carrito.'}, status=400)

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


def ver_carrito(request):
    carrito = Carrito(request)  # Inicializa la instancia de la clase Carrito con la solicitud actual
    carrito.calcular_subtotales()  # Calcula los subtotales para cada elemento del carrito
    contenido_carrito = carrito.carrito  # Obtén el contenido del carrito desde la instancia de la clase Carrito

    return render(request, 'carrito.html', {'contenido_carrito': contenido_carrito})

def enviar_carrito_por_whatsapp(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        email = request.POST['email']
        dni = request.POST['dni']
        carrito = Carrito(request)
        contenido_carrito = carrito.carrito

        mensaje = f"¡Hola! El cliente {nombre}, DNI:{dni}  (email: {email}) quisiera realizar el siguiente pedido:\n\n"
        total_carrito_usd = total_carrito(request)['total_carrito_usd']
        total_carrito_pesos = total_carrito(request)['total_carrito_pesos']
        
        for item in contenido_carrito.values():
            if item['tipo_moneda'] == "DOLARIZADO":
                mensaje += f"- Cod: {item['codigo']} - {item['nombre']} - Cantidad: {item['cantidad']} - Subtotal: USD{round(item['subtotal'], 2)}\n"
            else: 
                mensaje += f"- Cod: {item['codigo']} - {item['nombre']} - Cantidad: {item['cantidad']} - Subtotal: ${round(item['subtotal'], 2)}\n"
        mensaje += f"\n*Total del pedido: ${total_carrito_pesos} / USD{total_carrito_usd}*"

        # Número de teléfono al que se enviará el mensaje (debe estar en el formato internacional)
        numero_destino = '5491168713660'  # Reemplazar con el número del dueño del local

        # Codificar el mensaje para que sea una URL válida
        mensaje_codificado = quote(mensaje)

        # Construir el enlace de WhatsApp con el mensaje y el número de destino
        enlace_whatsapp = f"https://api.whatsapp.com/send?phone={numero_destino}&text={mensaje_codificado}"

        asunto = "Nuevo pedido recibido"
        destinatario = "Fdistribuidoradelsur@gmail.com"  # Reemplazar con el correo del dueño
        send_mail(
            asunto,
            mensaje,
            "Fdistribuidoradelsur@gmail.com",  # Reemplazar con el correo de la tienda
            [destinatario],
            fail_silently=False,
        )

        # Redirigir al usuario al enlace de WhatsApp
        return redirect(enlace_whatsapp)
    

def contact_form(request):  
    if request.method == "POST":
        nombre = request.POST['nombre']
        email = request.POST['email']
        mensaje = request.POST['mensaje']
        mensaje_html = "Nombre: {} \n Email: {} \n Mensaje: {}".format(nombre, email, mensaje)
        asunto = "Nuevo mensaje de contacto web"
        destinatario = "Fdistribuidoradelsur@gmail.com"
        send_mail (
            asunto,
            mensaje_html,
            "Fdistribuidoradelsur@gmail.com",
            [destinatario],
            fail_silently=False
        )
        context = {'mensaje_exito': '¡Mensaje enviado exitosamente!'}
        return render(request, 'home.html', context)
    return render(request, 'home.html', {})