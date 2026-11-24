
# Лабораторная работа №6 — Контейнеризация и CI: Docker, Docker Compose и GitHub Actions

Проект является продолжением лабораторной работы №5 по разработке микросервисной архитектуры на Python.

Два независимых микросервиса на FastAPI контейнеризированы с помощью Docker, объединены через Docker Compose и автоматически проверяются с помощью GitHub Actions.

## Репозитории проекта

- GitFlic: https://gitflic.ru/project/lilrax/lab6-docker-compose
- GitHub: https://github.com/lilrax/lab6-docker-compose
- GitHub Actions: https://github.com/lilrax/lab6-docker-compose/actions

[![lab6-ci](https://github.com/lilrax/lab6-docker-compose/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lilrax/lab6-docker-compose/actions/workflows/ci.yml)

## 1. Цель работы

Изучить технологии контейнеризации приложений, организовать совместный запуск микросервисов с помощью Docker Compose и настроить автоматический конвейер проверки и сборки проекта через GitHub Actions.

Основные задачи:

- Создать многостадийные Dockerfile.
- Уменьшить размер итоговых Docker-образов.
- Обеспечить запуск приложений от непривилегированного пользователя.
- Организовать взаимодействие микросервисов через сеть Docker.
- Настроить постоянное хранение данных.
- Реализовать healthcheck для обоих сервисов.
- Настроить конфигурацию через переменные окружения.
- Автоматизировать проверки Ruff, mypy и pytest.
- Настроить автоматическую сборку Docker-образов.

## 2. Описание проекта

Проект представляет собой систему из двух независимых Python-микросервисов, реализованных с помощью FastAPI.

Система предназначена для создания товаров и получения информации о них.

Каждый товар содержит:

- id — уникальный идентификатор;
- name — название товара;
- price — цена;
- quantity — количество.

### API Gateway

API Gateway является точкой входа для клиента.

Основные функции:

- Приём HTTP-запросов.
- Валидация входных данных.
- Проверка бизнес-правил.
- Взаимодействие со Storage Service.
- Обработка сетевых ошибок.
- Возвращение HTTP-ответов клиенту.

### Storage Service

Storage Service отвечает за хранение данных.

Основные функции:

- Создание товаров.
- Получение товаров по идентификатору.
- Работа с базой данных SQLite.
- Обеспечение сохранности данных.

API Gateway не обращается к базе данных напрямую. Все операции с данными выполняются через Storage Service.

## 3. Используемые технологии

| Технология | Назначение |
|---|---|
| Python 3.12 | Среда исполнения Docker и CI |
| FastAPI | Реализация REST API |
| Uvicorn | ASGI-сервер |
| Pydantic | Валидация данных |
| pydantic-settings | Управление конфигурацией |
| httpx | Межсервисное взаимодействие |
| SQLite | Хранение данных |
| Docker | Контейнеризация приложений |
| Docker Compose | Совместный запуск контейнеров |
| Docker Volume | Постоянное хранение данных |
| Ruff | Проверка качества кода |
| mypy | Статическая проверка типов |
| pytest | Автоматическое тестирование |
| pytest-cov | Измерение покрытия тестами |
| GitHub Actions | Автоматический конвейер CI |
| Git | Контроль версий |
| GitFlic | Основной репозиторий проекта |
| GitHub | Репозиторий для CI |

Локальные проверки в Windows выполнялись с Python 3.14.3.

В Docker-контейнерах и GitHub Actions используется Python 3.12.

## 4. Архитектура системы

```text
             Client / Swagger UI
                      |
                      | HTTP
                      | localhost:8080
                      v
+------------------------------------------+
|          Docker Compose Network          |
|                                          |
|   +----------------------------------+   |
|   |           API Gateway            |   |
|   |           gateway:8000           |   |
|   +----------------------------------+   |
|                    |                     |
|                    | HTTP / JSON         |
|                    v                     |
|   +----------------------------------+   |
|   |          Storage Service         |   |
|   |           storage:8001           |   |
|   +----------------------------------+   |
|                    |                     |
|                    v                     |
|   +----------------------------------+   |
|   |             SQLite               |   |
|   |       /app/data/items.db         |   |
|   +----------------------------------+   |
+--------------------|---------------------+
                     |
                     v
          +------------------------+
          |      Docker Volume     |
          |   lab6-storage-data    |
          +------------------------+
```

Внутри сети Docker API Gateway обращается к Storage Service по адресу:

```text
http://storage:8001
```

Вместо localhost используется имя сервиса Docker Compose.

Каждый микросервис содержит собственные зависимости, настройки, Dockerfile и автоматические тесты.

### Слоистая архитектура

В каждом сервисе выделены следующие слои:

- `api` — HTTP-маршруты, схемы и обработка запросов.
- `domain` — бизнес-логика, модели и интерфейсы.
- `storage` — реализация доступа к данным.

Используются следующие архитектурные паттерны:

- Repository Pattern.
- Dependency Injection.
- Ports and Adapters.

В API Gateway используется HttpItemRepository.

В Storage Service используется SQLiteItemRepository.

Подробное описание архитектуры находится в файле [docs/architecture.md](docs/architecture.md).

SQLite является встроенной файловой базой данных внутри Storage Service. Отдельный контейнер серверной СУБД в текущей реализации отсутствует. Доступ к хранилищу осуществляется через отдельный HTTP-микросервис, а постоянное хранение файла базы обеспечивается Docker Volume.

## 5. Структура проекта

```text
lab6-docker-compose/
|
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|
|-- api-gateway/
|   |-- app/
|   |   |-- api/
|   |   |-- domain/
|   |   |-- storage/
|   |   |-- config.py
|   |   `-- main.py
|   |
|   |-- tests/
|   |   |-- conftest.py
|   |   |-- test_api.py
|   |   |-- test_client.py
|   |   `-- test_domain.py
|   |
|   |-- .dockerignore
|   |-- .env.example
|   |-- Dockerfile
|   |-- mypy.ini
|   |-- requirements.txt
|   |-- requirements-dev.txt
|   `-- run.py
|
|-- storage/
|   |-- app/
|   |   |-- api/
|   |   |-- domain/
|   |   |-- storage/
|   |   |-- config.py
|   |   `-- main.py
|   |
|   |-- data/
|   |   `-- .gitkeep
|   |
|   |-- tests/
|   |   |-- conftest.py
|   |   |-- test_api.py
|   |   `-- test_domain.py
|   |
|   |-- .dockerignore
|   |-- .env.example
|   |-- Dockerfile
|   |-- mypy.ini
|   |-- requirements.txt
|   |-- requirements-dev.txt
|   `-- run.py
|
|-- docs/
|   `-- architecture.md
|
|-- .gitignore
|-- compose.yaml
`-- README.md
```

Локальная папка проекта может сохранять название `lab5-microservices-manual`, поскольку проект создан на основе предыдущей лабораторной работы.

## 6. Требования к окружению

Для запуска проекта через Docker необходимы:

- Docker Desktop или Docker Engine.
- Docker Compose v2.
- Git.
- Доступ к интернету для первоначальной сборки образов.

Установка Python на компьютер для контейнерного запуска не требуется.

Для локального запуска тестов необходим Python для Windows.

### Проверка Docker

```powershell
docker --version
docker compose version
docker info
```

### Проверка Python

```powershell
py -0p
```

При локальном выполнении лабораторной использовался Python 3.14.3.

## 7. Запуск проекта через Docker Compose

### 7.1. Клонирование репозитория

```powershell
git clone https://gitflic.ru/project/lilrax/lab6-docker-compose.git
cd lab6-docker-compose
```

Если проект уже скачан, достаточно открыть терминал в корневой папке проекта.

### 7.2. Создание Docker Volume

Перед первым запуском необходимо создать постоянный том для базы данных SQLite.

```powershell
docker volume create lab6-storage-data
```

Том используется для хранения базы данных независимо от жизненного цикла контейнеров.

### 7.3. Сборка и запуск контейнеров

```powershell
docker compose up --build -d --wait
```

Описание параметров:

- `--build` — сборка Docker-образов.
- `-d` — запуск контейнеров в фоновом режиме.
- `--wait` — ожидание готовности сервисов.

### 7.4. Проверка состояния контейнеров

```powershell
docker compose ps
```

Ожидаемый результат:

```text
SERVICE    STATUS
gateway    Up (healthy)
storage    Up (healthy)
```

Оба микросервиса должны иметь статус healthy.

### 7.5. Адреса сервисов

| Сервис | Адрес |
|---|---|
| API Gateway | http://localhost:8080 |
| API Gateway Swagger UI | http://localhost:8080/docs |
| API Gateway OpenAPI | http://localhost:8080/openapi.json |
| Storage Service | http://localhost:8001 |
| Storage Swagger UI | http://localhost:8001/docs |
| Storage OpenAPI | http://localhost:8001/openapi.json |

### 7.6. Просмотр логов

Просмотр логов всех контейнеров:

```powershell
docker compose logs
```

Просмотр логов в реальном времени:

```powershell
docker compose logs -f
```

Логи API Gateway:

```powershell
docker compose logs gateway
```

Логи Storage Service:

```powershell
docker compose logs storage
```

Для завершения просмотра логов используется Ctrl+C. Контейнеры при этом продолжают работать.

### 7.7. Остановка контейнеров

```powershell
docker compose down
```

Команда останавливает и удаляет контейнеры, но сохраняет данные во внешнем Docker Volume.

### 7.8. Повторный запуск

```powershell
docker compose up -d --wait
```

## 8. Dockerfile и безопасность

Для каждого микросервиса создан отдельный многостадийный Dockerfile.

### Стадия builder

На стадии сборки выполняется установка необходимых Python-зависимостей из requirements.txt.

### Финальная стадия

Финальная стадия использует базовый образ:

```dockerfile
FROM python:3.12-slim
```

В итоговый образ копируются только необходимые зависимости и исходный код приложения.

Это позволяет исключить ненужные инструменты разработки и уменьшить размер образа.

### Непривилегированный пользователь

Контейнеры запускаются от непривилегированного пользователя.

Приложения не выполняются от root.

Проверка пользователя:

```powershell
docker compose exec gateway id
docker compose exec storage id
```

Идентификатор пользователя UID должен отличаться от 0.

### Проверка размеров образов

```powershell
docker images lab6-gateway:latest
docker images lab6-storage:latest
```

Требование лабораторной работы — размер каждого финального Docker-образа не более 200 МБ.

Размер проверяется после сборки.

### Файлы .dockerignore

Для каждого сервиса используется собственный файл .dockerignore.

Из контекста сборки исключаются:

- Виртуальные окружения.
- Кэши Python.
- Локальные файлы конфигурации .env.
- Тесты.
- Служебные файлы Git.
- Другие ненужные для запуска файлы.

## 9. Конфигурация через переменные окружения

Настройки сервисов загружаются с помощью pydantic-settings.

В каждом микросервисе имеются файлы:

- `.env.example` — шаблон настроек.
- `app/config.py` — описание конфигурации.

Реальные файлы `.env` исключены из Git.

Docker Compose использует демонстрационные настройки из `.env.example` и переопределяет параметры, необходимые для работы внутри Docker.

### Настройки API Gateway

| Переменная | Значение в Docker |
|---|---|
| GATEWAY_HOST | 0.0.0.0 |
| GATEWAY_PORT | 8000 |
| GATEWAY_STORAGE_URL | http://storage:8001 |
| GATEWAY_REQUEST_TIMEOUT | 5 |
| GATEWAY_LOG_LEVEL | info |

### Настройки Storage Service

| Переменная | Значение в Docker |
|---|---|
| STORAGE_HOST | 0.0.0.0 |
| STORAGE_PORT | 8001 |
| STORAGE_DB_PATH | data/items.db |
| STORAGE_LOG_LEVEL | info |

Благодаря переменным окружения конфигурацию можно изменять без изменения исходного кода приложения.

## 10. Healthcheck и порядок запуска

Для обоих микросервисов настроена автоматическая проверка доступности.

Healthcheck выполняет HTTP-запрос к `/openapi.json` внутри соответствующего контейнера с помощью стандартной библиотеки Python urllib.request.

### Healthcheck Storage Service

```text
http://127.0.0.1:8001/openapi.json
```

### Healthcheck API Gateway

```text
http://127.0.0.1:8000/openapi.json
```

Параметры проверки:

| Параметр | Значение |
|---|---|
| interval | 5s |
| timeout | 3s |
| retries | 10 |
| start_period | 5s |

API Gateway запускается только после успешного прохождения healthcheck сервиса Storage.

Для этого используется:

```yaml
depends_on:
  storage:
    condition: service_healthy
```

Проверка состояния:

```powershell
docker compose ps
```

В ходе лабораторной работы оба контейнера успешно получили статус healthy.

Healthcheck подтверждает доступность HTTP-интерфейса приложения.

## 11. Постоянное хранение данных

Storage Service использует SQLite.

База данных внутри контейнера располагается по пути:

```text
/app/data/items.db
```

Для хранения используется внешний Docker Volume:

```text
lab6-storage-data
```

Конфигурация тома:

```yaml
volumes:
  storage_data:
    external: true
    name: lab6-storage-data
```

Том подключается к контейнеру Storage:

```yaml
volumes:
  - storage_data:/app/data
```

Это обеспечивает сохранение данных после:

- Остановки контейнеров.
- Перезапуска контейнеров.
- Удаления контейнеров.
- Пересоздания контейнеров.

Не следует удалять Docker Volume вручную, если необходимо сохранить данные.

### Проверка сохранности данных

1. Создать товар через API Gateway.
2. Запомнить идентификатор товара.
3. Остановить контейнеры:

```powershell
docker compose down
```

4. Повторно запустить контейнеры:

```powershell
docker compose up -d --wait
```

5. Получить ранее созданный товар по идентификатору.

Данные должны сохраниться.

## 12. REST API

Основные маршруты API Gateway:

| Метод | Маршрут | Назначение |
|---|---|---|
| POST | /items | Создание товара |
| GET | /items/{item_id} | Получение товара |
| GET | /docs | Swagger UI |
| GET | /openapi.json | OpenAPI-спецификация |

### Требования к данным

- Название товара должно быть непустым.
- Максимальная длина названия — 100 символов.
- Цена должна быть больше нуля.
- Количество должно быть целым неотрицательным числом.
- Идентификатор назначается автоматически.

### Создание товара через Swagger UI

Открыть:

```text
http://localhost:8080/docs
```

Выбрать POST /items, нажать Try it out и указать JSON:

```json
{
  "name": "Mouse",
  "price": 750,
  "quantity": 3
}
```

Ожидаемый HTTP-код:

```text
201 Created
```

Пример ответа:

```json
{
  "id": 1,
  "name": "Mouse",
  "price": 750,
  "quantity": 3
}
```

Идентификатор может отличаться в зависимости от содержимого базы данных.

### Получение товара

В Swagger UI выбрать:

```text
GET /items/{item_id}
```

Указать идентификатор, полученный при создании товара.

Ожидаемый результат:

```text
200 OK
```

### Проверка через PowerShell

Создание товара:

```powershell
$body = @{
    name = "PowerShellMouse"
    price = 2500
    quantity = 3
} | ConvertTo-Json

$item = Invoke-RestMethod `
    -Uri "http://localhost:8080/items" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$item
```

Получение товара:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8080/items/$($item.id)" `
    -Method Get
```

## 13. Обработка ошибок и устойчивость

Приложение корректно обрабатывает ошибки и возвращает соответствующие HTTP-коды.

| HTTP-код | Описание |
|---|---|
| 200 | Товар успешно получен |
| 201 | Товар успешно создан |
| 404 | Товар не найден |
| 422 | Некорректные входные данные |
| 502 | Некорректный ответ Storage Service |
| 503 | Storage Service недоступен |

### Проверка ошибки 404

Выполнить запрос:

```text
GET /items/999999
```

Ожидаемый результат:

```text
404 Not Found
```

### Проверка ошибки 422

Передать некорректные данные:

```json
{
  "name": "Mouse",
  "price": -100,
  "quantity": 5
}
```

Ожидаемый результат:

```text
422 Unprocessable Entity
```

### Проверка ошибки 503

Остановить только Storage Service:

```powershell
docker compose stop storage
```

Выполнить запрос через API Gateway.

Ожидаемый результат:

```text
503 Service Unavailable
```

API Gateway продолжает работать и корректно обрабатывает недоступность соседнего сервиса.

Повторно запустить Storage:

```powershell
docker compose up -d --wait storage
```

После восстановления Storage запрос существующего товара должен снова возвращать 200 OK.

Все сообщения приложения и журналы работы используют ASCII.

## 14. Локальные проверки качества кода

Для каждого микросервиса предусмотрено отдельное виртуальное окружение.

Проверки выполняются с помощью:

- Ruff — проверка качества кода.
- mypy — статическая проверка типов.
- pytest — автоматические тесты.

В локальном окружении Windows используется Python 3.14.3.

В Docker и GitHub Actions используется Python 3.12.

### 14.1. Проверка API Gateway

В корне проекта выполнить:

```powershell
cd .\api-gateway

py -3.14 -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

.\.venv\Scripts\python.exe -m ruff check .

.\.venv\Scripts\python.exe -m mypy .

.\.venv\Scripts\python.exe -m pytest -v
```

Результаты:

```text
All checks passed!
Success: no issues found in 18 source files
28 passed, 1 warning
```

Вернуться в корень проекта:

```powershell
cd ..
```

### 14.2. Проверка Storage Service

```powershell
cd .\storage

py -3.14 -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

.\.venv\Scripts\python.exe -m ruff check .

.\.venv\Scripts\python.exe -m mypy .

.\.venv\Scripts\python.exe -m pytest -v
```

Результаты:

```text
All checks passed!
Success: no issues found in 16 source files
18 passed, 1 warning
```

Вернуться в корень проекта:

```powershell
cd ..
```

### 14.3. Итоговые результаты тестирования

| Проверка | API Gateway | Storage Service |
|---|---|---|
| Ruff | Passed | Passed |
| mypy | Passed | Passed |
| pytest | 28 passed | 18 passed |

Всего успешно выполнено 46 автоматических тестов.

Предупреждение StarletteDeprecationWarning связано с используемыми библиотеками FastAPI и Starlette и не препятствует успешному выполнению тестов.

### 14.4. Настройка mypy

В каждом микросервисе создан файл mypy.ini.

```ini
[mypy]
plugins = pydantic.mypy
```

Плагин обеспечивает корректную статическую проверку моделей Pydantic и настроек BaseSettings.

### 14.5. Настройка тестового окружения

В папке tests каждого микросервиса создан файл conftest.py.

Он задаёт необходимые переменные окружения для автоматического запуска тестов.

Это позволяет выполнять тесты без ручного создания файлов .env.

Для Storage Service по умолчанию используется отдельная тестовая база данных test_storage.db.

Не следует передавать тестам настройки рабочей базы данных.

### 14.6. Проверка покрытия кода

В папке соответствующего микросервиса выполнить:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

## 15. GitHub Actions

Для автоматической проверки и сборки проекта настроен GitHub Actions.

Конфигурация расположена в файле:

```text
.github/workflows/ci.yml
```

Название конвейера:

```text
lab6-ci
```

Конвейер автоматически запускается:

- При отправке изменений в ветку main.
- При создании и обновлении Pull Request.

Используется среда ubuntu-latest и Python 3.12.

### Архитектура CI

```text
                 Git Push
                    |
                    v
               GitHub Actions
                    |
          +---------+---------+
          |                   |
          v                   v
      API Gateway        Storage Service
          |                   |
          v                   v
      Python 3.12         Python 3.12
          |                   |
          v                   v
      Create venv         Create venv
          |                   |
          v                   v
      Install deps        Install deps
          |                   |
          v                   v
         Ruff                Ruff
          |                   |
          v                   v
         mypy                mypy
          |                   |
          v                   v
        pytest              pytest
          |                   |
          v                   v
     Docker build        Docker build
          |                   |
          +---------+---------+
                    |
                    v
                 Success
```

### Этапы автоматического конвейера

| Этап | Назначение |
|---|---|
| Checkout repository | Получение исходного кода |
| Set up Python | Установка Python 3.12 |
| Install dependencies | Создание чистого venv и установка зависимостей |
| Ruff | Проверка качества кода |
| Mypy | Проверка типов |
| Pytest | Выполнение автоматических тестов |
| Docker build | Сборка Docker-образа |

Для каждого микросервиса создаётся отдельная задача через strategy.matrix.

Проверки выполняются независимо друг от друга.

При возникновении ошибки обязательного этапа соответствующая задача завершается со статусом Failure.

Сборка Docker-образа выполняется только после успешного прохождения предыдущих проверок соответствующего микросервиса.

### Результаты GitHub Actions

В ходе лабораторной работы были успешно выполнены автоматические конвейеры для обоих микросервисов.

Результаты доступны по ссылке:

https://github.com/lilrax/lab6-docker-compose/actions

Успешный запуск GitHub Actions подтверждает работоспособность автоматических проверок и сборки Docker-образов.

## 16. Запуск без Docker

При необходимости микросервисы можно запускать отдельно, как в лабораторной работе №5.

В этом случае API Gateway использует порт 8000 вместо 8080.

Для каждого сервиса необходимо создать виртуальное окружение и установить зависимости.

В папке каждого микросервиса создать .env из шаблона, если файл ещё отсутствует:

```powershell
Copy-Item .env.example .env
```

### Терминал №1 — Storage Service

```powershell
cd .\storage
.\.venv\Scripts\python.exe run.py
```

Адрес:

```text
http://127.0.0.1:8001/docs
```

### Терминал №2 — API Gateway

Из корня проекта:

```powershell
cd .\api-gateway
.\.venv\Scripts\python.exe run.py
```

Адрес:

```text
http://127.0.0.1:8000/docs
```

Для остановки процессов используется Ctrl+C.

Не следует одновременно запускать локальный Storage Service и Docker-контейнер Storage на одном порту 8001.

## 17. Git и публикация проекта

Основной репозиторий лабораторной работы расположен на GitFlic.

GitHub используется для выполнения автоматических проверок GitHub Actions.

В исходном локальном проекте настроены три удалённых репозитория.

| Remote | Назначение |
|---|---|
| origin | Лабораторная №5 на GitFlic |
| lab6 | Лабораторная №6 на GitFlic |
| github | Лабораторная №6 на GitHub |

Проверка удалённых репозиториев:

```powershell
git remote -v
```

Проверка состояния проекта:

```powershell
git status
```

Пример сохранения изменений:

```powershell
git add README.md

git commit -m "docs: update lab6 documentation"

git push lab6 main

git push github main
```

После отправки изменений в GitHub автоматически запускается GitHub Actions.

При новом клонировании репозитория имя удалённого репозитория может быть origin. Необходимо ориентироваться на результат команды git remote -v.

Изменения лабораторной №6 не должны отправляться в репозиторий лабораторной №5.

### Исключение локальных файлов из Git

Файл .gitignore исключает:

- .venv
- .env
- __pycache__
- .pytest_cache
- .mypy_cache
- .ruff_cache
- .coverage
- Файлы баз данных SQLite.

Шаблоны .env.example и файлы .gitkeep остаются в репозитории.

## 18. Возможные ошибки и решения

### Docker Engine недоступен

Необходимо запустить Docker Desktop.

Проверить состояние:

```powershell
docker info
```

### Docker Volume не найден

Создать необходимый том:

```powershell
docker volume create lab6-storage-data
```

### Контейнер не получает статус healthy

Проверить состояние и логи:

```powershell
docker compose ps
docker compose logs
```

### Порт уже занят

Необходимо остановить другой процесс или контейнер, использующий соответствующий порт.

Проверка контейнеров:

```powershell
docker ps
```

### В виртуальном окружении отсутствует Scripts

Причиной может быть использование Python из MSYS2.

Проверить доступные интерпретаторы:

```powershell
py -0p
where.exe python
```

Для создания Windows-окружения использовать обычный Python:

```powershell
py -3.14 -m venv .venv
```

### Отсутствуют обязательные переменные окружения

Для локального запуска необходимо создать .env из шаблона:

```powershell
Copy-Item .env.example .env
```

Для автоматических тестов настройки предоставляются файлами conftest.py.

### API Gateway возвращает 503

Необходимо проверить состояние Storage Service:

```powershell
docker compose ps
docker compose logs storage
```

### GitHub Actions не запускается

Необходимо проверить наличие файла:

```text
.github/workflows/ci.yml
```

И убедиться, что изменения отправлены именно на GitHub.

Отправка изменений только на GitFlic не запускает GitHub Actions.

## 19. Результаты выполнения лабораторной работы

В ходе выполнения лабораторной работы:

1. Контейнеризированы два микросервиса на FastAPI.
2. Созданы многостадийные Dockerfile.
3. Использован базовый образ python:3.12-slim.
4. Настроен запуск от непривилегированного пользователя.
5. Созданы файлы .dockerignore.
6. Настроен совместный запуск сервисов через Docker Compose.
7. Организовано взаимодействие сервисов через внутреннюю сеть Docker.
8. Настроено постоянное хранение SQLite через Docker Volume.
9. Реализован healthcheck для обоих микросервисов.
10. Настроена зависимость запуска через service_healthy.
11. Конфигурация вынесена в переменные окружения.
12. Успешно выполнены проверки Ruff.
13. Успешно выполнены проверки mypy.
14. Успешно выполнены 46 автоматических тестов.
15. Настроен автоматический конвейер GitHub Actions.
16. Подтверждена успешная автоматическая сборка Docker-образов.
17. Исходный код размещён на GitFlic и GitHub.
18. Подготовлена документация по запуску и проверке проекта.

## 20. Заключение

В ходе лабораторной работы были изучены технологии Docker, Docker Compose и GitHub Actions.

Приложение, разработанное в лабораторной работе №5, было контейнеризировано и адаптировано для совместного запуска микросервисов.

Docker Compose обеспечивает управление контейнерами, сетевое взаимодействие, проверку доступности сервисов и постоянное хранение данных.

GitHub Actions обеспечивает автоматическую проверку качества кода, аннотаций типов, выполнение тестов и сборку Docker-образов.

Оба микросервиса успешно запускаются в Docker-контейнерах и имеют статус healthy.

Все 46 локальных автоматических тестов успешно пройдены.

Автоматический конвейер GitHub Actions успешно выполнен.

Основной репозиторий проекта размещён на GitFlic.
