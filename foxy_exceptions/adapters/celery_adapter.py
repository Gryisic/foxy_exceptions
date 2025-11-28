def attach_celery_handler(app, notifier):
    try:
        from celery.signals import task_failure
    except ImportError:
        return

    @task_failure.connect
    def on_task_failure(sender=None, exception=None, traceback=None, **kwargs):
        notifier.notify(exception, context=sender.name)
