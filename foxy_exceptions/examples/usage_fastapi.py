from fastapi import FastAPI
from async_error_notifier import AsyncErrorNotifier, NotifierConfig
from async_error_notifier.adapters import NotifierMiddleware

config = NotifierConfig(endpoint_url="https://example.com/api/errors")
notifier = AsyncErrorNotifier(config)
notifier.start()

app = FastAPI()
app.add_middleware(NotifierMiddleware, notifier=notifier)


@app.get("/error")
async def error():
    raise RuntimeError("FastAPI test error")
