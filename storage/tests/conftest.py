
import os

# Устанавливаем настройки Storage для автоматических тестов.
# Если переменная уже задана, сохраняем её значение.
os.environ.setdefault("STORAGE_HOST", "127.0.0.1")
os.environ.setdefault("STORAGE_PORT", "8001")

# Используем отдельную тестовую базу данных,
# чтобы не затрагивать основные данные приложения.
os.environ.setdefault("STORAGE_DB_PATH", "test_storage.db")

# Задаём уровень журналирования.
os.environ.setdefault("STORAGE_LOG_LEVEL", "info")
