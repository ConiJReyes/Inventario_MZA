from django.contrib import admin
from .models import Producto, Kit, KitComponente, Lote

admin.site.register(Producto)
admin.site.register(Kit)
admin.site.register(Lote)
admin.site.register(KitComponente)