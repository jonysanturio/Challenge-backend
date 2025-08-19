# Ejecución del Programa

# Requisitos a tener en cuenta:
-Instalación de Python 3.10 o superior
-Obtener pip
-Redis Server

# Instalación de Redis
pip install redis (desde la terminal powershell)
sudo apt install redis-server(desde terminal de linux)
brew install redis (desde terminal Mac)

# Configuración del entorno virtual
python -m venv venv
# Para Linux o Mac
source venv/bin/activate  
# Para Windows
venv\Scripts\activate  

# Instalación de dependencias
pip install -r requirements.txt

# Ejecución del programa:
 1. En el archivo requirements.txt se encuentran las dependencias que se usan para la creación de la aplicación con fastapi, uvicorn, sqlalchemy, pydantic, se procede a instalar las dependencias con: pip install -r requirements.txt

 2. Iniciar la API: python -m uvicorn app.main:app --reload

# NOTA: Al iniciar la API desde la terminal nos econtraremos con una IP especifica de Uvicorn que se ejecuta de manera virtual desde venv. En si esa IP al iniciarla desde cualquier navegador no nos va a direccionar a la FastAPI, en ese caso debe seguir con el paso numero 3 para acceder correctamente a la documentación. 

 3. Acceder a la documentación: http://IP:8000/docs

# Ejecución de procesador de eventos distribuidos
python distributed/events.py -> Iniciarlo desde otra terminal para ver la sincronización de la latencia

# Ejecución de pruebas
pytest tests/ -v