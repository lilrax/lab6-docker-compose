
# ==========================================
# ПЕРВАЯ СТАДИЯ — BUILDER
# ==========================================

# Используем облегчённый образ Python 3.12.
# На этой стадии устанавливаем зависимости приложения.
# AS builder — название первой стадии.
FROM python:3.12-slim AS builder

# Создаём рабочую директорию внутри образа.
WORKDIR /app

# Копируем файл с зависимостями.
# Это позволяет Docker кэшировать слой установки библиотек.
COPY requirements.txt .

# Создаём виртуальное окружение Python.
# Устанавливаем необходимые библиотеки из requirements.txt.
#
# --no-cache-dir — не сохраняем кэш скачанных пакетов.
# --no-compile — не создаём скомпилированные файлы .pyc.
#
# После установки удаляем pip, так как для запуска
# приложения в готовом контейнере он больше не нужен.
#
# Дополнительно удаляем каталоги __pycache__,
# содержащие временные файлы Python.
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

# Создаём финальный образ из чистого Python 3.12-slim.
# В него не попадут инструменты первой стадии сборки.
FROM python:3.12-slim AS runtime

# Добавляем виртуальное окружение в системный PATH.
#
# PYTHONUNBUFFERED=1 — выводим логи сразу, без буферизации.
# PYTHONDONTWRITEBYTECODE=1 — запрещаем создание файлов .pyc.
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Создаём непривилегированного пользователя appuser.
# UID 10001 — его числовой идентификатор в Linux.
# Приложение не должно работать от имени root.
RUN useradd --create-home --uid 10001 appuser

# Копируем готовое виртуальное окружение из стадии builder.
# В нём уже находятся все библиотеки для работы приложения.
# pip и кэш Python были удалены на предыдущей стадии.
COPY --from=builder /opt/venv /opt/venv

# Указываем рабочую директорию приложения.
WORKDIR /app

# Копируем исходный код FastAPI внутрь контейнера.
# --chown назначает владельцем файлов пользователя appuser.
COPY --chown=appuser:appuser app/ ./app/

# Переключаемся на непривилегированного пользователя.
# Теперь приложение будет работать без прав root.
USER appuser

# Указываем, что приложение использует порт 8000.
# Сам EXPOSE не публикует порт на компьютере.
EXPOSE 8000

# Запускаем FastAPI с помощью сервера Uvicorn.
#
# app.main:app — объект FastAPI app в файле app/main.py.
# 0.0.0.0 — сервер принимает подключения через сеть контейнера.
# 8000 — порт, который прослушивает приложение.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
