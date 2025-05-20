from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('configuracion/', views.configuracion, name='configuracion'),
    path('productos-inventario/', views.productos_inventario, name='productos_inventario'),  # Ruta de inventario
    path('productos-inventario/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos-inventario/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

]
