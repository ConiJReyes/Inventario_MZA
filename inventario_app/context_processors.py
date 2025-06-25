# inventario_app/context_processors.py
def admin_check(request):
    print(f"Verificando usuario: {request.user.username}")  # Esto te confirmará que el context processor se ejecuta.
    
    if not request.user.is_authenticated:
        return {'es_admin': False , 'es_lector': False}

    es_admin = request.user.groups.filter(name='Administrador').exists()
    es_lector = request.user.groups.filter(name='Lectura').exists()

    print(es_admin)
    print(es_lector)
    
    return {
        'es_admin': es_admin,
        'es_lector': es_lector
    }




