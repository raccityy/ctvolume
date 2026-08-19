"""Pick polling or webhook from config.UPDATE_MODE."""

from __future__ import annotations

import config
import polling
import webhook


def start() -> None:
    mode = (config.UPDATE_MODE or "polling").strip().lower()
    if mode == "webhook":
        webhook.start()
    elif mode == "polling":
        polling.start()
    else:
        raise SystemExit(f"Unknown UPDATE_MODE={config.UPDATE_MODE!r}")
