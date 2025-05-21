from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('logout/', views.logout_view, name='logout'), 
    path('movimientos/', views.movimientos, name='movimientos'),
    path('reportes/', views.reportes_view, name='reportes'), 
    path('generar_reporte_word/', views.generar_reporte_word, name='generar_reporte_word'),
    path('productos-inventario/registrar/', views.registrar_producto, name='registrar_producto'),
    path('productos-inventario/', views.productos_inventario, name='productos_inventario'), 
    path('productos-inventario/editar/<int:pk>/', views.editar_producto_separado, name='editar_producto_separado'),  
    path('productos-inventario/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
]
