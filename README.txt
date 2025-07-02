===========================================
  Inventario - Maestranza Unidos S.A.
===========================================

Sistema de gestión de inventario con Django.

-------------------------------------------
👤 USUARIOS DE PRUEBA
-------------------------------------------

Administrador:
  Usuario: admin
  Correo:  maestranza@gmail.com
  Contraseña: admin123

Operario:
  Usuario: Operari1
  Correo:  Inv_Op1@gmail.com
  Contraseña: operario

-------------------------------------------
⚙️ CONFIGURACIÓN DEL ENTORNO
-------------------------------------------

1. Crear el entorno virtual:
   python -m venv venv

2. Activar el entorno virtual:
   venv\Scripts\activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Aplicar migraciones:
   python manage.py makemigrations
   python manage.py migrate

5. Ejecutar el servidor:
   python manage.py runserver
