from functools import wraps
from channels.db import database_sync_to_async

def database_sync_to_async_method(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        return await database_sync_to_async(method)(self, *args, **kwargs)
    return wrapper