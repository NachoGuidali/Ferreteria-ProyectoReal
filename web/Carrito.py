class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get('carrito')  # Utiliza el método get para obtener el valor de 'carrito'
        if carrito is None:  # Si 'carrito' no existe en la sesión, inicialízalo como un diccionario vacío
            carrito = {}
            self.session['carrito'] = carrito  # Asigna el diccionario vacío a la sesión
            self.carrito = carrito 
        else:
            self.carrito = carrito    


    def agregar(self, producto, cantidad=1):
        id = str(producto.id)
        if id not in self.carrito.keys():
            self.carrito[id]={
                'producto_id' : producto.id,
                'codigo' : producto.codigo, 
                'nombre' : producto.nombre,
                'cantidad' : cantidad,
                'precio' : producto.precio,
                'subtotal' : producto.precio * cantidad,
            }
        else:
            self.carrito[id]['cantidad'] += cantidad
            self.carrito[id]['subtotal'] += producto.precio * cantidad
        
        self.guardar_carrito()


    def guardar_carrito(self):
        self.session['carrito'] = self.carrito
        self.session.modified = True    

    def eliminar(self, producto):
        id = str(producto.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, producto):
        id = str(producto.id)
        if id in self.carrito.keys():
            self.carrito[id]['cantidad'] -= 1
            # self.carrito[id]['subtotal'] -= producto.precio
            if self.carrito[id]['cantidad'] <= 0: self.eliminar(producto)
            self.guardar_carrito()

    def limpiar(self):
        self.session['carrito'] = {}                  
        self.session.modified = True

    def calcular_subtotales(self):
        for item in self.carrito.values():
            if 'precio' in item and 'cantidad' in item:
                item['subtotal'] = round(item['precio'] * item['cantidad'])
  