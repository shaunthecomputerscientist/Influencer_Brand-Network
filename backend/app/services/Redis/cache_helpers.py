import json
from functools import wraps
from datetime import timedelta
from flask import current_app, jsonify, request, Response
import hashlib
from redis import StrictRedis
import redis



def configure_redis(app):
    # Initialize Redis with configuration from app config
    redis_instance = StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    app.config['REDIS_CLIENT'] = redis_instance
    try:
        redis_instance.ping()  # Test Redis connection
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
    return redis_instance

# Generate Cache Key function using SHA-256 hashing for unique identification
def generate_cache_key(path, *args, **kwargs):
    """Generates a hashed Redis cache key based on path and function arguments."""
    # Combine the path, args, and kwargs into a single string
    key_base = f"{path}:" + ":".join(str(arg) for arg in args) + ":" + ":".join(f"{k}-{v}" for k, v in kwargs.items())
    
    # Use SHA-256 to hash the combined key base
    key_hash = hashlib.sha256(key_base.encode()).hexdigest()
    return f"cache:{key_hash}"

# Caching Decorator
# Caching Decorator
def cache_data(expiration=timedelta(minutes=5)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate the cache key using request path and arguments
            cache_key = generate_cache_key(request.path, *args, **kwargs)
            
            # Check if the data exists in the cache
            cached_value = get_cache(cache_key)
            if cached_value is not None:
                print(cached_value)
                # Retrieve both data and status code from the cached value
                cached_data = cached_value.get("data")
                cached_status = cached_value.get("status")
                return jsonify(cached_data), cached_status
            
            # Execute the original route handler if not cached
            result = func(*args, **kwargs)
            print(result)
            response_obj, status_code = result if isinstance(result, tuple) else (result, 200)

            # Extract JSON data if it's a Response object with JSON content
            result_data = None
            if isinstance(response_obj, Response) and response_obj.is_json:
                result_data = response_obj.get_json()
            elif response_obj:
                result_data = response_obj  # Assume JSON-serializable if not a Response

            # Cache the result if JSON-serializable
            if result_data is not None:
                # Cache both the data and status code
                set_cache(cache_key, {"data": result_data, "status": status_code}, expiration=expiration)

            return response_obj if status_code is None else (response_obj, status_code)
        return wrapper
    return decorator




# Utility functions to interact with Redis
# Utility functions to interact with Redis
def set_cache(key, value, expiration=timedelta(hours=2)):
    """Sets a value in Redis with an expiration time in seconds."""
    redis_client = current_app.config['REDIS_CLIENT']
    # Serialize the value to JSON
    value_json = json.dumps(value)
    
    # Convert expiration to seconds
    expiration_seconds = int(expiration.total_seconds()) if isinstance(expiration, timedelta) else int(expiration)
    
    # Set cache with the expiration in seconds
    redis_client.setex(key, expiration_seconds, value_json)

def get_cache(key):
    """Gets a value from Redis and deserializes it from JSON."""
    redis_client = current_app.config['REDIS_CLIENT']
    value_json = redis_client.get(key)
    return json.loads(value_json) if value_json else None

def cache_exists(key):
    """Checks if a cache key exists in Redis."""
    redis_client = current_app.config['REDIS_CLIENT']
    return redis_client.exists(key) > 0