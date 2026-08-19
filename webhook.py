"""Hosted update transport — Telegram webhook + FastAPI."""

from __future__ import annotations

import logging
import os

import config
import logutil
from bot_instance import bot

_LISTEN = "0.0.0.0"
_PATH = "telegram"
_MAX_CONNECTIONS = 40


def resolved_base_url() -> str:
    host = (os.environ.get("RENDER_EXTERNAL_HOSTNAME") or "").strip()
    candidates = [
        (config.WEBHOOK_URL or "").strip(),
        (os.environ.get("RENDER_EXTERNAL_URL") or "").strip(),
        f"https://{host}" if host else "",
    ]
    for raw in candidates:
        if raw.lower().startswith("https://"):
            return raw.split("?")[0].rstrip("/")
    return ""


def _port() -> int:
    raw = (os.environ.get("PORT") or "").strip()
    if raw.isdigit():
        return int(raw)
    return 10000


def is_hosted() -> bool:
    if resolved_base_url():
        return True
    return (os.environ.get("PORT") or "").strip().isdigit()


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

    base = resolved_base_url()
    public_url = ""
    if base:
        public_url = base if base.endswith(f"/{_PATH}") else f"{base}/{_PATH}"
    port = _port()

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

    app.add_api_route(f"/{_PATH}", _process, methods=["POST"])
    app.add_api_route(f"/{_PATH}/", _process, methods=["POST"])

    if public_url:
        bot.set_webhook(
            url=public_url,
            max_connections=_MAX_CONNECTIONS,
            drop_pending_updates=True,
            secret_token=None,
        )
        logutil.info(f"Webhook set → {public_url}")
    else:
        logutil.error("HTTP is up but no public URL — Telegram webhook not set")
    logutil.info(f"Bot is running — {_LISTEN}:{port}/{_PATH}")

    uvicorn.run(
        app,
        host=_LISTEN,
        port=port,
        log_level="warning",
        access_log=False,
    )
