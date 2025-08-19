# ----Objetivo del challenge:------
 El presente challenge tiene como finalidad crear un sistema que sea coherente y escalable para gestionar productos de forma centralizada, y que múltiples tiendas se sincronicen en su inventario en tiempo real. A su vez contiene operaciones CRUD básicas sobre una base de datos relacional. A su vez se tienen que manejar los alto tráfico, baja latencia y coherencia de datos en un sistema distribuido.

# ------Manejo de herramientas:-------
 Base de datos: SQLite 
 Backend**: FastAPI → API REST 
 Estructura modular: separación de capas (models, schemas, crud, main)


## 🏗️ Arquitectura propuesta
1. **API REST** para exponer operaciones CRUD.
2. **Base de datos principal** (PostgreSQL).
3. **Cache distribuida** (Redis) para mejorar la latencia de lecturas frecuentes.
4. **Replicación y particionado** de datos para manejar escalabilidad horizontal.
5. **Consistencia eventual** en caso de concurrencia alta (lecturas pueden estar levemente desactualizadas pero priorizan la performance).

# ------Tecnologías utilizadas:--------
 1. Python 3.10 o Superior -> Lenguaje Principal
 2. FastAPI -> Framework para la API REST
 3. SQLAlchemy -> ORM para manejo de base de datos
 4. Pydantic -> Para validar los datos 
 5. SQLite -> Base de datos 
 6. Uvicorn -> ASGI server
 7. Swagger UI -> para la documentación interactiva
 8. Redis -> Para caché distribuida
 9. Pytest -> Para realizar testing


# -------Problema de Latencia y Coherencia:-------
- Una sola base de datos centralizada no soporta alto tráfico.
- El sistema incorpora:
  - Cache para disminuir la latencia.
  - Estrategias de sincronización para mantener la coherencia de datos.
  - Posible uso de CQRS para separar las cargas de lectura y escritura.
