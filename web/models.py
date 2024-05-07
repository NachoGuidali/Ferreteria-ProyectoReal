from django.db import models

# Create your models here.
class Producto(models.Model):
    codigo = models.CharField(max_length=15)
    nombre = models.CharField(max_length=50)
    proveedor = models.CharField(max_length=50)
    tipo_moneda = models.CharField(max_length=50)
    precio = models.FloatField()

    def __str__(self):
        return self.nombre