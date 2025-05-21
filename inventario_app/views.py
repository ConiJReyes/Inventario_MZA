from docx import Document
from django.http import HttpResponse
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
        
        user = authenticate(request, username=correo, password=contrasena)
        
        if user is not None:
            login(request, user)  
            return redirect('dashboard')  
        else:
            return render(request, 'inventario_app/login.html', {'error': 'Credenciales incorrectas'}) 

    return render(request, 'inventario_app/login.html')  

def logout_view(request):
    logout(request)  
    return redirect('login')  

@staff_member_required
def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        confirmar = request.POST.get('confirmar')
        rol = request.POST.get('rol')  

        if contrasena != confirmar:
            return render(request, 'inventario_app/registro.html', {'error': 'Las contraseñas no coinciden'})

        if User.objects.filter(username=correo).exists():
            return render(request, 'inventario_app/registro.html', {'error': 'Correo ya registrado'})

        usuario = User.objects.create_user(username=correo, email=correo, password=contrasena, first_name=nombre)

        
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

        user_id = request.POST.get('user_id')
        usuario = get_object_or_404(User, pk=user_id)
        rol = request.POST.get('roles')  
        
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


#REPORTES 


@login_required
def reportes_view(request):
    # Obtener los movimientos registrados
    movimientos = Movimiento.objects.all().order_by('-fecha')
    
    # También puedes agregar las ventas cuando se implementen
    # ventas = Venta.objects.all()  # Asegúrate de tener un modelo de ventas cuando lo implementes

    return render(request, 'inventario_app/reportes.html', {
        'movimientos': movimientos,
        'movimientos_count': movimientos.count(),
        # 'ventas': ventas,  # Incluye las ventas cuando las implementes
    })


#REPORTES
@login_required
def reportes_view(request):
    # Obtener todos los movimientos registrados
    movimientos = Movimiento.objects.all().order_by('-fecha')

    # Contar el total de movimientos
    movimientos_count = movimientos.count()

    return render(request, 'inventario_app/reportes.html', {
        'movimientos': movimientos,
        'movimientos_count': movimientos_count,
    })

# Generar el reporte en Word
@login_required
def generar_reporte_word(request):
    # Obtener todos los movimientos
    movimientos = Movimiento.objects.all()

    # Crear un nuevo documento Word
    doc = Document()

    # Agregar un título
    doc.add_heading('Reporte de Movimientos de Inventario', 0)

    # Crear la tabla con los movimientos
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'

    # Encabezados de la tabla
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Producto'
    hdr_cells[1].text = 'Tipo de Movimiento'
    hdr_cells[2].text = 'Cantidad'
    hdr_cells[3].text = 'Fecha'

    # Llenar la tabla con los movimientos
    for movimiento in movimientos:
        row_cells = table.add_row().cells
        row_cells[0].text = movimiento.producto.nombre
        row_cells[1].text = movimiento.tipo_movimiento
        row_cells[2].text = str(movimiento.cantidad)
        row_cells[3].text = str(movimiento.fecha)

    # Crear la respuesta HTTP con el archivo Word
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="movimientos.docx"'

    # Guardar el archivo Word en la respuesta HTTP
    doc.save(response)
    return response



#REGISTRAR PRODUCTOS
@login_required
def registrar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        stock = request.POST.get('stock')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')  # Obtiene la imagen si es que se sube

        # Crear el nuevo producto
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            stock=stock,
            precio=precio,
            imagen=imagen
        )

        return redirect('productos_inventario')  # Redirige a la lista de productos después de crear

    return render(request, 'inventario_app/registrar_producto.html')  # Muestra el formulario para agregar un nuevo producto