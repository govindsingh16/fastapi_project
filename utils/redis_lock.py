from core.redis import redis_client


def acquire_lock(key: str, timeout: int = 5):
    return redis_client.set(key, "locked", nx=True, ex=timeout)


def release_lock(key: str):
    redis_client.delete(key)