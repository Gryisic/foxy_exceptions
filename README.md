# 🦊 Foxy Exceptions

Универсальная библиотека для отправки ошибок из Python-приложений. Поддерживает **async/sync**, очередь, retry, dedupe и адаптеры под Celery / FastAPI / Django. Работает в worker-ах, backend-ах, cron-ах и CLI-скриптах.

## ✨ Возможности

- Асинхронный `AsyncErrorNotifier` и синхронный `SyncErrorNotifier`
- Очередь + авто-retry
- Dedupe (не шлёт одинаковые ошибки)
- Настраиваемая конфигурация: TTL, headers, timeout, retries
- HTTP-клиенты: aiohttp / requests
- Фреймворк-адаптеры (опционально, без жёстких зависимостей)

## 📦 Установка

```sh
pip install foxy-exceptions
```

# 🚀 Быстрый старт

## Async

```python
import asyncio
from foxy_exceptions import AsyncErrorNotifier, NotifierConfig

async def main():
    notifier = AsyncErrorNotifier(
        NotifierConfig(
            endpoint_url="http://localhost:8080/exception",
            project="demo",
            environment="prod",
        )
    )

    notifier.start()

    try:
        1 / 0
    except Exception as exc:
        await notifier.notify("worker", exc)

    await notifier.stop()

asyncio.run(main())
```

## Sync

```python
from foxy_exceptions import SyncErrorNotifier, NotifierConfig

notifier = SyncErrorNotifier(
    NotifierConfig(
        endpoint_url="http://localhost:8080/exception",
        project="demo",
        environment="prod",
    )
)

try:
    raise RuntimeError("boom")
except Exception as exc:
    notifier.notify("script", exc)

notifier.stop()
```

## 📡 Формат отправки

```json
{
  "project": "demo",
  "environment": "prod",
  "source": "worker",
  "error": "Exception",
  "traceback": "Traceback...",
  "meta": {}
}
```

# 🧩 Celery (через адаптер)

```python
from foxy_exceptions.adapters import attach_celery_handler
from foxy_exceptions import AsyncErrorNotifier, NotifierConfig

notifier = AsyncErrorNotifier(NotifierConfig(...))
notifier.start()

app = ...  

attach_celery_handler(app, notifier)
```
