from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    stock = models.IntegerField(default=0)  # Stock total, suma de lotes
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.BooleanField(default=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)  # Fecha de vencimiento general (opcional)

    def __str__(self):
        return self.nombre

    def actualizar_stock(self):
        # Actualiza el stock total sumando cantidades de todos los lotes asociados
        total = self.lotes.aggregate(total_stock=models.Sum('cantidad'))['total_stock'] or 0
        self.stock = total
        self.save()



# Nuevo modelo de lotes, mandale el caso al chat y preguntale sobre los lotes, pero en resumen son agrupaciones de
# piezas(productos) entonces eso, es medio confuso
class Lote(models.Model):
    producto = models.ForeignKey(Producto, related_name='lotes', on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    fecha_vencimiento = models.DateField(null=True, blank=True)  # Fecha específica por lote
    marca = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.nombre}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Al guardar lote, actualizar el stock total del producto padre
        self.producto.actualizar_stock()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.producto.actualizar_stock()

#conjunto de piezas
class Kit(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    piezas = models.ManyToManyField(Producto, through='KitComponente')
    stock = models.IntegerField(default=0)  # Stock calculado basado en componentes (mínimo posible)

    def __str__(self):
        return self.nombre

    def actualizar_stock(self):
        # El stock de un kit depende de las piezas componentes y sus cantidades.
        # Calcular el máximo de kits que se pueden armar según el stock de cada pieza
        cantidades = []
        for componente in self.kitcomponentes.all():
            if componente.cantidad > 0:
                posible = componente.producto.stock // componente.cantidad
                cantidades.append(posible)
            else:
                cantidades.append(0)
        self.stock = min(cantidades) if cantidades else 0
        self.save()

#cosas de cada kit
class KitComponente(models.Model):
    kit = models.ForeignKey(Kit, related_name='kitcomponentes', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ('kit', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.kit.nombre}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.kit.actualizar_stock()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.kit.actualizar_stock()


class Movimiento(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_movimiento = models.CharField(max_length=7, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo_movimiento.capitalize()} - {self.producto.nombre} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Podrías actualizar aquí stocks y validaciones según movimiento


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
