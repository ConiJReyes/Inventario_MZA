from django.contrib import admin
from django.urls import path, include

# Importar settings y static para servir media
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventario_app.urls')),  # todo a inventario_app
]

# Agregar esta parte para que Django sirva media cuando DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
