
from django import forms
from .models import Producto

class CargarProductosForm(forms.Form):
    archivo_excel = forms.FileField()
    # class Meta:
    #     model = Producto
    #     fields = ['archivo_excel']
