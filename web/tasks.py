# tasks.py
import os
import pandas as pd
from celery import shared_task
from .models import Producto
from django.db import transaction
from django.conf import settings

# @shared_task
# def procesar_archivo_excel(ruta_archivo):
#     try:
#         df = pd.read_excel(ruta_archivo, skiprows=8)
#         Producto.objects.all().delete()
#         for index, row in df.iterrows():
#             Producto.objects.create(
#                 codigo=row['Codigo'],
#                 nombre=row['Producto'],
#                 proveedor=row['Marca'],
#                 tipo_moneda=row['TipoMoneda'],
#                 precio=row['Precio'],
#             )
#         # Eliminar el archivo Excel después de procesar
#         os.remove(ruta_archivo)    
#     except Exception as e:
#         print(f"Error al procesar el archivo Excel: {str(e)}")

@shared_task
def procesar_archivo_excel(ruta_archivo):
    try:
        df = pd.read_excel(ruta_archivo, skiprows=8)
        Producto.objects.all().delete()
        
        batch_size = 1000
        productos = []

        for index, row in df.iterrows():
            producto = Producto(
                codigo=row['Codigo'],
                nombre=row['Producto'],
                proveedor=row['Marca'],
                tipo_moneda=row['TipoMoneda'],
                precio=row['Precio'],
            )
            productos.append(producto)
            
            if len(productos) == batch_size:
                with transaction.atomic():
                    Producto.objects.bulk_create(productos)
                productos = []

        # Guardar los productos restantes
        if productos:
            with transaction.atomic():
                Producto.objects.bulk_create(productos)

        # Eliminar el archivo Excel después de procesar
        os.remove(ruta_archivo)
        
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {str(e)}")
