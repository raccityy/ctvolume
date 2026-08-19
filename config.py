"""Hardcoded settings — nothing is read from env."""

BOT_NAME = "ClearTactics Volume Bot"
BOT_SHORT = "ClearTactics"

TELEGRAM_BOT_TOKEN = "8756023350:AAG02mliXM7BUEoECZdPerm1xfX-tnXJunQ"

PAYMENT_WALLET = "7ZFqJAjGfxgRacCZwE1yqoFkrQGdZznqfVbxA4tBHPXh"
PAYMENT_CURRENCY = "SOL"
PAYMENT_NETWORK = "Solana"

MIN_DEPOSIT = 0.01
MIN_WITHDRAWAL = 0.01
DEPOSIT_PRESETS = [0.5, 1.0, 2.5, 5.0]

SUPPORT_HANDLE = "@Mr_Nexisx"
SUPPORT_URL = "https://t.me/Mr_Nexisx"

ADMIN_GROUP_CHAT_ID = "-5392153689"

# polling  = local / default
# webhook  = hosted (fill WEBHOOK_URL, then set UPDATE_MODE = "webhook")
UPDATE_MODE = "polling"
WEBHOOK_URL = "https://your-service.onrender.com"
WEBHOOK_LISTEN = "0.0.0.0"
WEBHOOK_PORT = 10000
WEBHOOK_PATH = "telegram"
WEBHOOK_MAX_CONNECTIONS = 40
