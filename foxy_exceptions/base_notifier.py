from typing import Any


class BaseNotifier:
    def _normalize_source(self, source: Any) -> str:
        if isinstance(source, str):
            return source

        name = getattr(source, "name", None)
        if isinstance(name, str):
            return name

        cls = source.__class__.__name__
        try:
            rep = repr(source)
            if len(rep) > 120:
                rep = rep[:117] + "..."
            return f"{cls}: {rep}"
        except Exception:
            return cls
