from django.utils.deprecation import MiddlewareMixin
from ..notifier_async import AsyncErrorNotifier
import asyncio


class DjangoNotifierMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None, notifier: AsyncErrorNotifier = None):
        super().__init__(get_response)
        self.notifier = notifier

    def process_exception(self, request, exception):
        if self.notifier:
            asyncio.create_task(self.notifier.notify(exception, context=str(request.path)))
        return None
