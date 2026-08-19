"""Hosted update transport — Telegram webhook + FastAPI."""

from __future__ import annotations

import logging

import config
import logutil
from bot_instance import bot


def start() -> None:
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
        import uvicorn
        from telebot.types import Update
    except ImportError as err:
        raise SystemExit(
            "Install webhook deps: pip install fastapi uvicorn\n"
            f"{err}"
        ) from err

    raw = (config.WEBHOOK_URL or "").strip()
    if not raw.lower().startswith("https://"):
        raise SystemExit("WEBHOOK_URL in config.py must be a public https:// URL")

    base = raw.split("?")[0].rstrip("/")
    path = (config.WEBHOOK_PATH or "telegram").strip().strip("/")
    public_url = base if base.endswith(f"/{path}") else f"{base}/{path}"

    logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    app = FastAPI(redirect_slashes=False)

    @app.get("/")
    async def health() -> dict:
        return {"ok": True}

    async def _process(request: Request):
        try:
            payload = await request.json()
            update = Update.de_json(payload)
            if update:
                bot.process_new_updates([update])
        except Exception as err:
            logutil.error(f"Update handler failed: {err}")
        return JSONResponse(content={"ok": True}, status_code=200)

    app.add_api_route(f"/{path}", _process, methods=["POST"])
    app.add_api_route(f"/{path}/", _process, methods=["POST"])

    bot.set_webhook(
        url=public_url,
        max_connections=int(config.WEBHOOK_MAX_CONNECTIONS),
        drop_pending_updates=True,
        secret_token=None,
    )
    logutil.info(f"Webhook set → {public_url}")
    logutil.info(
        f"Bot is running — {config.WEBHOOK_LISTEN}:{config.WEBHOOK_PORT}/{path}"
    )

    uvicorn.run(
        app,
        host=config.WEBHOOK_LISTEN,
        port=int(config.WEBHOOK_PORT),
        log_level="warning",
        access_log=False,
    )
