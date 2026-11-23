
# Настраиваем переменные окружения для автоматических тестов.
import os

# Значения используются только в том случае,
# если соответствующие переменные ещё не установлены.
os.environ.setdefault("GATEWAY_HOST", "127.0.0.1")
os.environ.setdefault("GATEWAY_PORT", "8000")
os.environ.setdefault("GATEWAY_STORAGE_URL", "http://127.0.0.1:8001")
os.environ.setdefault("GATEWAY_REQUEST_TIMEOUT", "5")
os.environ.setdefault("GATEWAY_LOG_LEVEL", "info")
