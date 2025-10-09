import asyncio

def async_wrapper(async_fn):
    def wrapper(data):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(async_fn(data))
        except RuntimeError:
            asyncio.run(async_fn(data))
    return wrapper
