from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..notifier_async import AsyncErrorNotifier


class NotifierMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, notifier: AsyncErrorNotifier):
        super().__init__(app)
        self.notifier = notifier

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            await self.notifier.notify(exc, context=request.url.path)
            raise
