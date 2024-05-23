# tasks.py
from celery import shared_task
import pandas as pd
from .models import Producto
import os

@shared_task
def procesar_archivo_excel(ruta_archivo):
    try:
        df = pd.read_excel(ruta_archivo, skiprows=8)
        Producto.objects.all().delete()
        for index, row in df.iterrows():
            Producto.objects.create(
                codigo=row['Codigo'],
                nombre=row['Producto'],
                proveedor=row['Marca'],
                tipo_moneda=row['TipoMoneda'],
                precio=row['Precio'],
            )
        # Eliminar el archivo Excel después de procesar
        os.remove(ruta_archivo)    
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {str(e)}")
