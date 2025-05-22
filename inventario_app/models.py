# inventario_app/models.py

from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    stock = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.BooleanField(default=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)  # Fecha de vencimiento del producto

    def __str__(self):
        return self.nombre



class Movimiento(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=7, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo_movimiento.capitalize()} - {self.producto.nombre} - {self.cantidad} piezas"
