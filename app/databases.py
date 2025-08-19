from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
import redis

DATABASES_URL = "sqlite:///./products.db"

engine = create_engine(DATABASES_URL, connect_args= {"check_same_thread" : False}) #En python con la base de datos va con un solo hilo y con funciones y con diferentes hilos y peticiones van a hacer referencias a la base de datos

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base() #unifica la creacion de las tablas y las clases dependiendo sus estados


redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=3, retry_on_timeout=True)






