from django.urls import path
from .views import cargar_productos, lista_productos, home, agregar_al_carrito, restar_producto, vaciar_carrito, eliminar_del_carrito, ver_carrito, enviar_carrito_por_whatsapp
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('', home, name='home'),
    path('productos', lista_productos, name='productos'),
    path('cargar', cargar_productos, name='cargar'),
    path('agregar/<int:producto_id>', agregar_al_carrito, name='agregar_al_carrito'),
    path('restar/<int:producto_id>', restar_producto, name='restar_producto'),
    path('eliminar/<int:producto_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('vaciar-carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('carrito', ver_carrito, name='carrito'),
    path('enviar-carrito/', enviar_carrito_por_whatsapp, name='enviar_carrito_por_whatsapp'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    
]