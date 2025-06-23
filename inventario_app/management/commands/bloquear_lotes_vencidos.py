from django.core.management.base import BaseCommand
from inventario_app.models import Lote
from inventario_app.models import Notificacion  
from django.contrib.auth.models import User
from datetime import date

class Command(BaseCommand):
    help = 'Bloquea automáticamente los lotes vencidos'

    def handle(self, *args, **kwargs):
        hoy = date.today()
        lotes_vencer = Lote.objects.filter(fecha_vencimiento__lt=hoy, estado='activo')
        admin_users = User.objects.filter(is_superuser=True)

        for lote in lotes_vencer:
            lote.estado = 'bloqueado'
            lote.save()

            for admin in admin_users:
                Notificacion.objects.create(
                    usuario=admin,
                    mensaje=f"El lote {lote.numero_lote} del producto {lote.producto.nombre} ha sido bloqueado por vencimiento."
                )

        self.stdout.write(self.style.SUCCESS('Lotes vencidos bloqueados correctamente.'))
