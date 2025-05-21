from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from .models import Movimiento, Producto  
from django.contrib.auth import logout


def home(request):
    return render(request, 'inventario_app/home.html')

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']
        
        # Intentar autenticar al usuario con el correo como username
        user = authenticate(request, username=correo, password=contrasena)
        
        if user is not None:
            login(request, user)  # Iniciar sesión para el usuario
            return redirect('dashboard')  # Redirige al dashboard después de un login exitoso
        else:
            return render(request, 'inventario_app/login.html', {'error': 'Credenciales incorrectas'})  # Mostrar error si no se puede autenticar

    return render(request, 'inventario_app/login.html')  # Mostrar la página de login en GET

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige a la página de login después de cerrar sesión

@staff_member_required
def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        confirmar = request.POST.get('confirmar')
        rol = request.POST.get('rol')  # Captura el rol enviado desde el formulario

        if contrasena != confirmar:
            return render(request, 'inventario_app/registro.html', {'error': 'Las contraseñas no coinciden'})

        if User.objects.filter(username=correo).exists():
            return render(request, 'inventario_app/registro.html', {'error': 'Correo ya registrado'})

        usuario = User.objects.create_user(username=correo, email=correo, password=contrasena, first_name=nombre)

        # Asignar grupo según rol seleccionado
        if rol:
            grupo = Group.objects.filter(name=rol).first()
            if grupo:
                usuario.groups.add(grupo)

        return redirect('dashboard')

    return render(request, 'inventario_app/registro.html')

@login_required
def dashboard(request):
    return render(request, 'inventario_app/dashboard.html')



#PARA EL CRUD DE LOS PRODUCTOS
#VISTA PARA LISTAR LOS PRODUCTOS
@login_required
def productos_inventario(request):
    productos = Producto.objects.all()
    return render(request, 'inventario_app/productos_inventario.html', {'productos': productos})

#VISTA PARA EDITARLOS

@login_required
def editar_producto_separado(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.stock = request.POST['stock']
        producto.precio = request.POST['precio']

        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']

        producto.save()
        return redirect('productos_inventario')

    return render(request, 'inventario_app/editar_inventario.html', {'producto': producto})

#VISTA PARA ELIMINAR U PRODUCTO
@login_required
@require_POST
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()  # elimina de la base de datos
    return redirect('productos_inventario')

#PAGINA DEL CONFIGURACION
@login_required
def configuracion(request):
    if request.method == 'POST':
        # Captura el usuario
        user_id = request.POST.get('user_id')
        usuario = get_object_or_404(User, pk=user_id)
        rol = request.POST.get('roles')  # Captura los roles enviados
        
        # Lógica para prevenir que el administrador cambie su rol
        if 'Administrador' in rol and 'Administrador' not in [grupo.name for grupo in usuario.groups.all()]:
            return render(request, 'inventario_app/configuracion.html', {
                'error': 'No puedes asignar el rol de Administrador.',
                'usuarios': User.objects.all(),
            })

        usuario.groups.set(rol)
        usuario.save()

    return render(request, 'inventario_app/configuracion.html', {'usuarios': User.objects.all()})

@login_required
@require_POST
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.delete()
    return redirect('configuracion')


#MOVIMIENTOS
@login_required
def movimientos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        tipo_movimiento = request.POST.get('tipo_movimiento')
        cantidad = int(request.POST.get('cantidad'))  # Convertir a entero

        producto = Producto.objects.get(id=producto_id)
        
        if tipo_movimiento == 'entrada':
            producto.stock += cantidad  # Agregar al stock
        elif tipo_movimiento == 'salida':
            if producto.stock >= cantidad:  # Verificar que haya suficiente stock
                producto.stock -= cantidad  # Restar del stock
            else:
                return render(request, 'inventario_app/movimientos.html', {
                    'error': 'No hay suficiente stock para la salida',
                    'productos': Producto.objects.all()
                })

        producto.save()

        # Crear el registro del movimiento
        Movimiento.objects.create(
            producto=producto,
            tipo_movimiento=tipo_movimiento,
            cantidad=cantidad,
            usuario=request.user  # Guardar el usuario que realizó el movimiento
        )

        return redirect('movimientos')  # Redirige a la misma página para ver los movimientos

    movimientos = Movimiento.objects.all().order_by('-fecha')
    productos = Producto.objects.all()  # Para mostrar los productos en el formulario
    return render(request, 'inventario_app/movimientos.html', {
        'movimientos': movimientos,
        'movimientos_count': movimientos.count(),
        'productos': productos
    })

