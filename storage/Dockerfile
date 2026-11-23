
# ==========================================
# ПЕРВАЯ СТАДИЯ — BUILDER
# ==========================================

# Используем облегчённый образ Python версии 3.12.
# В этой стадии устанавливаем библиотеки для Storage Service.
FROM python:3.12-slim AS builder

# Указываем рабочую папку для установки зависимостей.
WORKDIR /build

# Копируем файл со списком необходимых библиотек.
COPY requirements.txt .

# Создаём виртуальное окружение Python.
# Устанавливаем библиотеки без кэша и компиляции .pyc.
# После установки удаляем pip и временные файлы,
# чтобы уменьшить размер итогового Docker-образа.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --no-compile -r requirements.txt \
    && rm -rf /opt/venv/lib/python3.12/site-packages/pip \
              /opt/venv/lib/python3.12/site-packages/pip-*.dist-info \
              /opt/venv/bin/pip \
              /opt/venv/bin/pip3 \
              /opt/venv/bin/pip3.12 \
    && find /opt/venv -type d -name __pycache__ -prune -exec rm -rf {} +


# ==========================================
# ВТОРАЯ СТАДИЯ — RUNTIME
# ==========================================

# Создаём финальный образ для запуска Storage Service.
FROM python:3.12-slim AS runtime

# Добавляем виртуальное окружение в PATH.
# Сразу выводим логи и отключаем создание файлов .pyc.
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Создаём пользователя appuser без прав root.
# Создаём папку для базы данных SQLite.
# Разрешаем пользователю appuser записывать данные в /app/data.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

# Переносим установленные библиотеки из первой стадии.
COPY --from=builder /opt/venv /opt/venv

# Устанавливаем рабочую папку приложения.
WORKDIR /app

# Копируем Python-код Storage Service в контейнер.
# Назначаем владельцем файлов пользователя appuser.
COPY --chown=appuser:appuser app/ ./app/

# Запускаем приложение от обычного пользователя.
USER appuser

# Указываем внутренний порт Storage Service.
EXPOSE 8001

# Запускаем FastAPI с помощью Uvicorn.
# app.main:app — приложение из файла app/main.py.
# 0.0.0.0 — разрешает сетевые подключения внутри Docker.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
