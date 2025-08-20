from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker 
import redis

DATABASES_URL = "sqlite:///./products.db"

engine = create_engine(DATABASES_URL, connect_args= {"check_same_thread" : False}) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base() 

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=3)






