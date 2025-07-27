import time
from functools import wraps
import logging

def retry_with_backoff(max_attempts: int, backoff_in_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(backoff_in_seconds * 2 ** (attempts - 1))
                    logging.warning(f"Retry {attempts}/{max_attempts} for {func.__name__}")
        return wrapper
    return decorator