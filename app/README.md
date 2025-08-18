# ----Objetivo del challenge:------
# El presente challenge tiene como finalidad crear un sistema que sea coherente y escalable para gestionar productos de forma centralizada, y que múltiples tiendas se sincronicen en su inventario en tiempo real

# -----Funcionalidad de la aplicación:------
# 1- Crear productos
# 2- Leer productos
# 3- Actualizar stocks y precios
# 4- Eliminar productos
# 5- Validar datos
# 6- Manejo de error HTTP estándar

# ------Manejo de herramientas:-------
# Base de datos: SQLite 
# Backend**: FastAPI → API REST 
# Estructura modular: separación de capas (models, schemas, crud, main)


# ------Ejecución del programa:-------
# 1. En el archivo requirements.txt se encuentran las dependencias que se usan para la creación de la aplicación con fastapi, uvicorn, sqlalchemy, pydantic, se procede a instalar las dependencias con: pip install -r requirements.txt

# 2. Iniciar la API: python -m uvicorn app.main:app --reload

# NOTA: Al iniciar la API desde la terminal nos econtraremos con una IP especifica de Uvicorn que se ejecuta de manera virtual desde venv. En si esa IP al iniciarla desde cualquier navegador no nos va a direccionar a la FastAPI, en ese caso debe seguir con el paso numero 3 para acceder correctamente a la documentación. 
# 3. Acceder a la documentación: http://IP:8000/docs


# ------Tecnologías utilizadas:--------
# 1. Python -> Lenguaje Principal
# 2. FastAPI -> Framework para la API REST
# 3. SQLAlchemy -> ORM para manejo de base de datos
# 4. Pydantic -> Para validar los datos 
# 5. SQLite -> Base de datos 
# 6. Uvicorn -> ASGI server
# 7. Swagger UI -> para la documentación interactiva

