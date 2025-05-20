from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from inventario_app.models import Producto

def home(request):
    return render(request, 'inventario_app/home.html')

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']
        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'inventario_app/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'inventario_app/login.html')


@staff_member_required
def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        confirmar = request.POST.get('confirmar')

        if contrasena != confirmar:
            return render(request, 'inventario_app/registro.html', {'error': 'Las contraseñas no coinciden'})

        if User.objects.filter(username=correo).exists():
            return render(request, 'inventario_app/registro.html', {'error': 'Correo ya registrado'})

        User.objects.create_user(username=correo, email=correo, password=contrasena, first_name=nombre)
        return redirect('dashboard')

    return render(request, 'inventario_app/registro.html')


@login_required
def dashboard(request):
    return render(request, 'inventario_app/dashboard.html')


@login_required
def configuracion(request):
    # Lógica para la vista de configuración
    return render(request, 'inventario_app/configuracion.html')



@login_required
def productos_inventario(request):
    # Aquí podrías obtener los productos desde la base de datos
    # Por ejemplo: productos = Producto.objects.all()
    
    productos = [
        {"nombre": "Producto A", "stock": 100, "precio": 10.0},
        {"nombre": "Producto B", "stock": 50, "precio": 25.0},
        {"nombre": "Producto C", "stock": 200, "precio": 5.5},
    ]  # Simulamos los productos

    return render(request, 'inventario_app/productos_inventario.html', {'productos': productos})



#PARA EL CRUD DE LOS PRODUCTOS

#VISTA PARA LISTAR LOS PRODUCTOS
@login_required
def productos_inventario(request):
    productos = Producto.objects.all()
    editar_id = request.GET.get('editar')
    producto_a_editar = None
    if editar_id:
        producto_a_editar = get_object_or_404(Producto, pk=editar_id)

    if request.method == 'POST':
        pk = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, pk=pk)
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.stock = request.POST['stock']
        producto.precio = request.POST['precio']
        producto.save()
        return redirect('productos_inventario')

    return render(request, 'inventario_app/productos_inventario.html', {
        'productos': productos,
        'producto_a_editar': producto_a_editar
    })


#VISTA PARA EDITARLOS

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.stock = request.POST['stock']
        producto.precio = request.POST['precio']
        producto.save()

        return JsonResponse({
            'success': True,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'stock': producto.stock,
            'precio': producto.precio
        })

    return render(request, 'inventario_app/editar_producto.html', {'producto': producto})


#VISTA PARA ELIMINAR U PRODUCTO
@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('productos_inventario')
