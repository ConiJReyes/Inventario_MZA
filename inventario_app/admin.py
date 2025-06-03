from django.contrib import admin
from .models import Producto, Kit, KitComponente

admin.site.register(Producto)
admin.site.register(Kit)
admin.site.register(KitComponente)