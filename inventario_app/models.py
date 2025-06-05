from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    stock = models.IntegerField(default=0)  # Stock total, suma de lotes
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

# Nuevo modelo de lotes
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
        self.producto.actualizar_stock()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.producto.actualizar_stock()

# Modelo de kits
class Kit(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    piezas = models.ManyToManyField(Producto, through='KitComponente')
    stock = models.IntegerField(default=0)  # Stock calculado basado en componentes (mínimo posible)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def actualizar_stock(self):
        cantidades = []
        for componente in self.kitcomponentes.all():
            if componente.cantidad > 0:
                posible = componente.producto.stock // componente.cantidad
                cantidades.append(posible)
            else:
                cantidades.append(0)
        self.stock = min(cantidades) if cantidades else 0
        self.save()

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

# Modelo de movimiento
class Movimiento(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )
    TIPO_ELEMENTO = (
        ('pieza', 'Pieza'),
        ('lote', 'Lote'),
        ('kit', 'Kit'),
    )

    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, null=True, blank=True, on_delete=models.SET_NULL)
    tipo_elemento = models.CharField(max_length=10, choices=TIPO_ELEMENTO, default='pieza')
    tipo_movimiento = models.CharField(max_length=7, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    motivo_movimiento = models.CharField(default=True)

    def __str__(self):
        if self.tipo_elemento == 'kit':
            return f"{self.tipo_movimiento.capitalize()} - {self.producto.nombre} - {self.cantidad} kits"
        return f"{self.tipo_movimiento.capitalize()} - {self.producto.nombre} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        if self.tipo_elemento == 'kit' and self.tipo_movimiento == 'salida':
            self.descontar_piezas_del_kit()
        if self.tipo_elemento == 'lote' and self.tipo_movimiento == 'salida':
            self.descontar_piezas_del_lote()
        super().save(*args, **kwargs)

    def descontar_piezas_del_kit(self):
        kit = Kit.objects.get(id=self.producto.id)
        for componente in kit.kitcomponentes.all():
            producto = componente.producto
            cantidad_a_descontar = componente.cantidad * self.cantidad  # Descontamos según la cantidad de kits
            producto.stock -= cantidad_a_descontar  # Descontamos del stock de cada pieza
            producto.save()
        kit.estado = False  # Marcar el kit como inactivo
        kit.save()

    def descontar_piezas_del_lote(self):
        lote = Lote.objects.get(id=self.lote.id)
        producto = lote.producto
        cantidad_a_descontar = self.cantidad  # Descontamos según la cantidad de lote
        producto.stock -= cantidad_a_descontar
        producto.save()
        lote.save()



class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
