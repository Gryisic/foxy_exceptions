import asyncio
from foxy_exceptions import AsyncErrorNotifier, NotifierConfig


async def main():
    config = NotifierConfig(
        endpoint_url="http://localhost:8080/exception",
        project="my_project",
        environment="prod",
    )

    notifier = AsyncErrorNotifier(config)
    notifier.start()

    try:
        1 / 0
    except Exception as exc:
        await notifier.notify("test", exc)

    await asyncio.sleep(1)
    await notifier.stop()


if __name__ == "__main__":
    asyncio.run(main())
