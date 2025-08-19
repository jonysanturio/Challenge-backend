import json
from typing import List
from .databases import redis_client
from .models import Product
from .import Logger
from databases import datetime
import uuid

def publish_inventory(event_type : str, product : Product, stores : List[str] = None):
    event = {
        "event_id" : str(uuid.uuid4()),
        "event_type" : event_type,
        "product_id" : product.id,
        "name" : product.name,
        "stock" : product.stock,
        "price" : product.price,
        "timestamp" : datetime.utcnow().isoformat(),
        "affected_stores" : stores or []
    }
    try:
        redis_client.publish("inventory_events", json.dump(event))
        for store_id in (stores or []):
            redis_client.publish(f"store_{store_id}_events", json.dumps(event))
    except Exception as e:
        Logger.error(f"Error en el evento: {str(e)}")
        
def get_event_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("inventory_events")
    return pubsub
