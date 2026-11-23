# Лабораторная работа №5 — Микросервисы на Python

## 1. Описание проекта

Проект представляет собой систему из двух независимых Python-микросервисов, реализованных с помощью FastAPI. Сервисы взаимодействуют по HTTP в формате JSON.

Система предназначена для создания товаров и получения информации о них. Каждый товар имеет идентификатор `id`, название `name`, цену `price` и количество `quantity`.

В проект входят:

- **API Gateway** — точка входа для клиента. Принимает HTTP-запросы, проверяет входные данные, применяет бизнес-правила и вызывает Storage Service.
- **Storage Service** — сервис хранения данных. Принимает запросы от API Gateway и сохраняет товары в базе данных SQLite.

Каждый сервис запускается в отдельном процессе, имеет собственные зависимости, настройки, виртуальное окружение и тесты.

**Репозиторий GitFlic:** https://gitflic.ru/project/lilrax/lab5-microservices-manual

## 2. Используемые технологии

| Технология | Назначение |
|---|---|
| Python 3 | Язык программирования; при итоговой проверке использовался Python 3.14.3 |
| FastAPI | Реализация REST API обоих микросервисов |
| Uvicorn | ASGI-сервер для запуска приложений |
| Pydantic | Описание и валидация моделей запросов и ответов |
| pydantic-settings | Чтение и проверка конфигурации из `.env` и переменных окружения |
| httpx | HTTP-клиент для связи API Gateway со Storage Service |
| SQLite (`sqlite3`) | Постоянное хранение товаров в отдельном файле БД |
| pytest | Автоматическое тестирование |
| pytest-cov | Измерение покрытия кода тестами |
| Ruff | Проверка стиля, импортов и форматирование кода |
| Git / GitFlic | Контроль версий и публикация проекта |

## 3. Архитектура и взаимодействие сервисов

```text
                      HTTP / JSON
Клиент (браузер, Swagger UI, PowerShell)
                       |
                       v
             +--------------------+
             |    API Gateway     |
             |   127.0.0.1:8000   |
             |  api -> domain ->  |
             | HTTP client (httpx)|
             +--------------------+
                       |
                       | HTTP / JSON, timeout
                       v
             +--------------------+
             |   Storage Service  |
             |   127.0.0.1:8001   |
             |  api -> domain ->  |
             | SQLite repository  |
             +--------------------+
                       |
                       v
                 SQLite database
                storage/data/items.db
```

Порядок обработки создания товара:

1. Клиент отправляет `POST /items` в API Gateway на порт `8000`.
2. Pydantic проверяет формат входного JSON.
3. Доменный слой API Gateway проверяет бизнес-правила.
4. HTTP-клиент на `httpx` отправляет запрос в Storage Service на порт `8001`.
5. Storage Service сохраняет запись в SQLite и возвращает созданный товар с `id`.
6. API Gateway возвращает клиенту согласованный JSON-ответ и код `201 Created`.

При чтении товара выполняется аналогичная цепочка через `GET /items/{item_id}`. API Gateway не обращается к SQLite напрямую: за данные отвечает Storage Service.

Подробное объяснение границ и слоёв приведено в [docs/architecture.md](docs/architecture.md).

## 4. Структура проекта

```text
lab5-microservices-manual/
|-- .gitignore
|-- README.md
|-- docs/
|   `-- architecture.md
|-- api-gateway/
|   |-- .env.example
|   |-- requirements.txt
|   |-- run.py
|   |-- app/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- main.py
|   |   |-- api/
|   |   |   |-- __init__.py
|   |   |   |-- routes.py
|   |   |   `-- schemas.py
|   |   |-- domain/
|   |   |   |-- __init__.py
|   |   |   |-- errors.py
|   |   |   |-- models.py
|   |   |   |-- ports.py
|   |   |   `-- services.py
|   |   `-- storage/
|   |       |-- __init__.py
|   |       `-- client.py
|   `-- tests/
|       |-- test_api.py
|       |-- test_client.py
|       `-- test_domain.py
`-- storage/
    |-- .env.example
    |-- requirements.txt
    |-- run.py
    |-- app/
    |   |-- __init__.py
    |   |-- config.py
    |   |-- main.py
    |   |-- api/
    |   |   |-- __init__.py
    |   |   |-- routes.py
    |   |   `-- schemas.py
    |   |-- domain/
    |   |   |-- __init__.py
    |   |   |-- models.py
    |   |   |-- ports.py
    |   |   `-- services.py
    |   `-- storage/
    |       |-- __init__.py
    |       `-- repository.py
    |-- data/
    |   `-- .gitkeep
    `-- tests/
        |-- test_api.py
        `-- test_domain.py
```

При настройке проекта локально также создаются `api-gateway/.venv/`, `storage/.venv/`, файлы `.env`, `.coverage`, кэши инструментов и `storage/data/items.db`. Они не должны попадать в Git и исключены через `.gitignore`. Файл `.gitkeep` сохраняет пустую папку `data` в репозитории.

## 5. Требования к окружению

Для запуска понадобятся:

- Windows 10/11 с Windows PowerShell;
- установленный Python 3 и Python Launcher (`py`);
- Git (для клонирования и обновления проекта);
- доступ к интернету при первоначальной установке зависимостей.

**Важно:** на компьютере, где проводилась последняя проверка, команда `py -3 --version` показала **Python 3.14.3**. Проект и оба набора тестов были успешно запущены на этой версии.

`py -3` означает «выбрать установленный Python 3», а не «обязательно Python 3.10 или 3.12». На другом компьютере будет выбрана версия, доступная через Python Launcher. Конкретную версию всегда проверяйте перед созданием окружения.

### 5.1. Проверка версии Python

Откройте Windows PowerShell:

```powershell
py --list
py -3 --version
```

Ожидаемый результат для компьютера, на котором выполнялась проверка:

```text
Python 3.14.3
```

В данном проекте **не требуется команда** `py -3.12`: на проверяемой машине такая версия не была зарегистрирована в Python Launcher.

### 5.2. Важное замечание для Windows: MSYS и виртуальные окружения

На проверяемом компьютере обычная команда `python` указывала на:

```text
C:\msys64\ucrt64\bin\python.exe
```

При выполнении `python -m venv .venv` создавалось окружение с Unix-структурой (`bin`, `include`, `lib`) вместо Windows-структуры с `Scripts`. Поэтому путь `.\.venv\Scripts\python.exe` не существовал.

**Рабочее решение:** для создания виртуальных окружений использовать `py -3 -m venv .venv`, а затем вызывать Python из созданного окружения по прямому пути `.\.venv\Scripts\python.exe`.

Это исключает случайное использование другого Python из `PATH`.

## 6. Установка и настройка в Windows PowerShell

Ниже приведены команды, по которым проект был успешно запущен после скачивания из GitFlic. Команды выполняются отдельно для каждого микросервиса.

### 6.1. Получение проекта

Если репозиторий ещё не скачан:

```powershell
cd C:\Users\admin\Downloads
git clone https://gitflic.ru/project/lilrax/lab5-microservices-manual.git
cd .\lab5-microservices-manual
```

Если папка проекта уже скачана, клонировать её повторно не нужно. Перейдите прямо в её корень:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual
```

**Примечание:** `C:\Users\admin\Downloads\...` — пример фактического пути с проверочного компьютера. Если проект находится в другой папке, замените путь на свой.

### 6.2. Настройка Storage Service (порт 8001)

В корне проекта выполните:

```powershell
cd .\storage
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Команду `Copy-Item` достаточно выполнить один раз. Если `.env` уже существует и содержит ваши настройки, не перезаписывайте его без необходимости.

Проверьте окружение:

```powershell
Test-Path .\.venv\Scripts\python.exe
```

Результат `True` означает, что Windows-интерпретатор виртуального окружения найден.

Настройки Storage Service хранятся в файле `storage/.env` и считываются с помощью `pydantic-settings`. Для локальной демонстрации сервис должен запускаться по адресу `127.0.0.1:8001`; файл базы данных расположен в `storage/data/`.

### 6.3. Настройка API Gateway (порт 8000)

После настройки Storage Service перейдите из папки `storage` в `api-gateway`:

```powershell
cd ..\api-gateway
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Проверка окружения:

```powershell
Test-Path .\.venv\Scripts\python.exe
```

В `api-gateway/.env` настраиваются адрес и порт Gateway, URL соседнего сервиса, таймаут HTTP-запроса и уровень логирования. При локальном запуске используются такие значения:

| Настройка API Gateway | Значение |
|---|---|
| `GATEWAY_HOST` | `127.0.0.1` |
| `GATEWAY_PORT` | `8000` |
| `GATEWAY_STORAGE_URL` | `http://127.0.0.1:8001` |
| `GATEWAY_REQUEST_TIMEOUT` | `5.0` |
| `GATEWAY_LOG_LEVEL` | `info` |

Исходные значения и фактические имена параметров для каждого сервиса находятся в соответствующих `.env.example` и `app/config.py`. Можно вывести шаблон командой `Get-Content .env.example` из папки нужного сервиса.

Активация `.venv` через `Activate.ps1` **не обязательна**: все дальнейшие команды непосредственно используют интерпретатор из виртуального окружения.

## 7. Запуск микросервисов

**Для работы системы нужны два одновременно запущенных терминала PowerShell.** Каждый сервис запускается из собственной папки и занимает свой порт.

### Терминал №1 — Storage Service

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\storage
.\.venv\Scripts\python.exe run.py
```

Ожидаемый фрагмент журнала:

```text
Uvicorn running on http://127.0.0.1:8001
Application startup complete.
```

Не закрывайте терминал: процесс Storage Service должен продолжать работать.

### Терминал №2 — API Gateway

Откройте **новую вкладку PowerShell**:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\api-gateway
.\.venv\Scripts\python.exe run.py
```

Ожидаемый фрагмент журнала:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Не закрывайте и этот терминал, пока выполняете запросы.

### Проверка запуска в браузере

| Сервис | Swagger UI | OpenAPI JSON |
|---|---|---|
| API Gateway | http://127.0.0.1:8000/docs | http://127.0.0.1:8000/openapi.json |
| Storage Service | http://127.0.0.1:8001/docs | http://127.0.0.1:8001/openapi.json |

Открывайте именно страницу `/docs`. Ответ `404 Not Found` на `/` или `/favicon.ico` не означает, что API сломан: для этих путей просто не предусмотрены обработчики.

Для остановки каждого сервиса нажмите `Ctrl + C` в терминале, где он работает.

## 8. REST API и модели данных

Основные пользовательские операции API Gateway:

| Метод | Маршрут | Назначение | Успешный код |
|---|---|---|---|
| `POST` | `/items` | Создать товар | `201 Created` |
| `GET` | `/items/{item_id}` | Получить товар по идентификатору | `200 OK` |
| `GET` | `/docs` | Открыть Swagger UI | `200 OK` |
| `GET` | `/openapi.json` | Получить спецификацию OpenAPI | `200 OK` |

### Модель создания товара

```json
{
  "name": "MicroserviceMouse",
  "price": 3500,
  "quantity": 4
}
```

Требования к данным:

- `name` — непустая строка длиной не более 100 символов;
- `price` — число строго больше нуля;
- `quantity` — целое неотрицательное число;
- `id` — идентификатор, назначаемый сервером, а не передаваемый клиентом при создании.

Пример ответа сервера:

```json
{
  "name": "MicroserviceMouse",
  "price": 3500,
  "quantity": 4,
  "id": 1
}
```

Идентификатор `id` может отличаться: это зависит от текущего содержимого базы данных.

## 9. Сквозная проверка через Swagger UI

Это фактически выполненная проверка двух микросервисов.

### 9.1. Создание товара — POST

1. Убедитесь, что работают Storage Service (`8001`) и API Gateway (`8000`).
2. Откройте http://127.0.0.1:8000/docs.
3. Найдите `POST /items` и нажмите **Try it out**.
4. Укажите JSON:

   ```json
   {
     "name": "MicroserviceMouse",
     "price": 3500,
     "quantity": 4
   }
   ```

5. Нажмите **Execute**.
6. Убедитесь, что сервер вернул **`201 Created`** и объект с полем `id`.

На проверочном компьютере ответ содержал `id: 1`. В логах обоих серверов появилась запись:

```text
POST /items HTTP/1.1 201 Created
```

### 9.2. Получение товара — GET

1. На той же странице Swagger UI найдите `GET /items/{item_id}`.
2. Нажмите **Try it out**.
3. Введите `item_id`, полученный при создании (в данном примере — `1`).
4. Нажмите **Execute**.

Ожидаемый ответ — **`200 OK`** с теми же данными:

```json
{
  "name": "MicroserviceMouse",
  "price": 3500,
  "quantity": 4,
  "id": 1
}
```

В журналах работы сервисов была подтверждена цепочка:

```text
GET /items/1 HTTP/1.1 200 OK
```

Это подтверждает успешный межсервисный обмен по HTTP: клиент отправляет запрос в Gateway, Gateway обращается к Storage Service, а Storage Service читает запись из SQLite.

## 10. Сквозная проверка через PowerShell

В **третьем терминале PowerShell** можно выполнить запросы без браузера. Первые два терминала с серверами при этом должны оставаться запущенными.

Создать товар:

```powershell
$body = @{
    name = "PowerShellMouse"
    price = 2500
    quantity = 3
} | ConvertTo-Json

$item = Invoke-RestMethod -Uri "http://127.0.0.1:8000/items" -Method Post -ContentType "application/json" -Body $body
$item
```

Получить созданный товар по идентификатору:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/items/$($item.id)" -Method Get
```

Проверить несуществующий товар:

```powershell
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/items/999999" -Method Get
} catch {
    Write-Host "HTTP request failed as expected: $($_.Exception.Message)"
}
```

Для успешного создания ожидается `201`, для чтения — `200`, для отсутствующего товара — `404`. Код HTTP можно посмотреть в Swagger UI или в терминалах серверов.

### Дополнительно: пример curl

Следующий пример предназначен для Bash/Git Bash или Linux/macOS:

```bash
curl -i -X POST http://127.0.0.1:8000/items \
  -H 'Content-Type: application/json' \
  -d '{"name":"CurlMouse","price":2000,"quantity":2}'

curl -i http://127.0.0.1:8000/items/1
```

При использовании второго запроса замените `1` на идентификатор из ответа `POST`.

## 11. Проверка ошибок и устойчивости

API Gateway обрабатывает ошибки предсказуемо и возвращает соответствующий HTTP-код вместо необработанного исключения.

| Ситуация | Код | Пояснение |
|---|---|---|
| Товар создан | `201` | Объект записан в SQLite |
| Товар найден | `200` | Данные получены из Storage Service |
| Запрошенный товар не существует | `404` | Ресурс не найден |
| Некорректные входные данные | `422` | Ошибка валидации |
| Storage Service недоступен | `503` | Gateway не может связаться с соседом |
| Storage Service вернул недопустимый ответ | `502` | Gateway получил ошибочный ответ от соседнего сервиса |

### 11.1. Проверка 404 Not Found

В Swagger UI вызовите `GET /items/999999`. Ожидается `404 Not Found`.

### 11.2. Проверка 422 Unprocessable Entity

В `POST /items` укажите некорректное значение, например:

```json
{
  "name": "Mouse",
  "price": -100,
  "quantity": 5
}
```

Ожидается `422`, потому что цена должна быть положительной. Для `GET /items/0` также ожидается `422`, так как идентификатор должен быть больше нуля.

### 11.3. Проверка 503 Service Unavailable

1. Убедитесь, что оба сервиса первоначально работают.
2. Остановите **только Storage Service** (`Ctrl + C` в терминале с портом `8001`).
3. Оставьте API Gateway на порту `8000` запущенным.
4. Повторите запрос `GET /items/1` через http://127.0.0.1:8000/docs.

Ожидается ответ:

```json
{
  "detail": "storage service unavailable"
}
```

HTTP-код: **`503 Service Unavailable`**. В логах Gateway появляется понятная запись о недоступности Storage Service, без падения самого Gateway.

5. Запустите Storage Service повторно:

   ```powershell
   cd C:\Users\admin\Downloads\lab5-microservices-manual\storage
   .\.venv\Scripts\python.exe run.py
   ```

6. Повторите `GET /items/1`. Если товар остался в базе данных, ответ снова будет `200 OK`.

Такое поведение (`200` → `503` → `200`) было продемонстрировано при проверке проекта.

## 12. Слоистая архитектура и паттерны

В каждом микросервисе выделены три слоя:

- **`api/`** — HTTP-маршруты FastAPI, Pydantic-схемы, преобразование ошибок в HTTP-ответы.
- **`domain/`** — модели предметной области и бизнес-правила, независимые от FastAPI и SQLite.
- **`storage/`** — адаптеры доступа к данным: HTTP-клиент в Gateway и SQLite-репозиторий в Storage Service.

Домен определяет интерфейс репозитория через `typing.Protocol` (`ItemRepository`). Конкретная реализация внедряется извне. В Storage Service используется `SQLiteItemRepository`, в Gateway — `HttpItemRepository`, а в тестах — поддельные реализации без реальной сети и БД.

Так реализованы **Ports and Adapters**, **Repository Pattern** и **Dependency Injection**. Создание FastAPI-приложения и сборка зависимостей происходят через `create_app()` в `app/main.py`.

Принципиальное разделение ответственности:

- Gateway отвечает за внешний API, проверку и маршрутизацию запросов.
- Storage Service отвечает за операции с данными и их сохранность.
- Только Storage Service имеет доступ к SQLite.
- Оба сервиса можно запускать и тестировать независимо.

## 13. Конфигурация и логирование

У каждого сервиса есть собственные `app/config.py` и `.env.example`. Для локального запуска создаётся `.env`, настройки загружаются через `BaseSettings` из `pydantic-settings`.

В частности, Gateway получает из конфигурации адрес Storage Service и таймаут HTTP-вызова. Это позволяет изменять окружение, не редактируя исходный код клиента.

Важные особенности:

- `httpx` использует явный таймаут (при локальной проверке — `5.0` секунды).
- Сетевые сбои переводятся в понятную ошибку недоступности соседнего сервиса.
- Некорректные ответы соседа обрабатываются отдельно.
- Уровень логирования задаётся настройками.
- `.env` не публикуется в Git; для других пользователей сохраняется `.env.example`.

В логи пишутся текстовые ASCII-сообщения. При недоступности Storage Service Gateway продолжает работать и возвращает управляемый ответ `503`.

## 14. Автоматическое тестирование

Тесты каждого сервиса выполняются **отдельно**, из его собственной папки, с Python его виртуального окружения. Для проверки тестов не требуется запускать оба Uvicorn-процесса.

### 14.1. Тесты Storage Service

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\storage
.\.venv\Scripts\python.exe -m pytest tests -v
```

Результат итоговой проверки:

```text
18 passed, 1 warning
```

Тестируются доменные правила, HTTP API, валидация, чтение и запись данных в SQLite, а также сохранность данных при создании нового экземпляра репозитория.

### 14.2. Тесты API Gateway

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\api-gateway
.\.venv\Scripts\python.exe -m pytest tests -v
```

Результат итоговой проверки:

```text
28 passed, 1 warning
```

Тесты проверяют домен, маршруты FastAPI и HTTP-клиент на `httpx`, в том числе обработку `404`, `422`, `500`, `503`, таймаутов, сетевых ошибок и неверного ответа соседнего сервиса.

**Суммарно: 46 успешно пройденных тестов.**

### 14.3. Предупреждение StarletteDeprecationWarning

При запуске обоих наборов тестов наблюдалось предупреждение библиотеки FastAPI/Starlette:

```text
StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead.
```

Это **предупреждение об изменениях зависимости, а не провал тестов**. Оно возникало в коде установленной библиотеки `fastapi.testclient` и не помешало выполнению тестов. Итоговый статус проверки — `passed`.

### 14.4. Покрытие кода

Для Storage Service:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\storage
.\.venv\Scripts\python.exe -m pytest tests --cov=app --cov-report=term-missing
```

Результат: **99% покрытия** (по итоговому запуску).

Для API Gateway:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\api-gateway
.\.venv\Scripts\python.exe -m pytest tests --cov=app --cov-report=term-missing
```

Результат: **95% покрытия** (по итоговому запуску).

Покрытие — доля выполненных операторами тестов строк кода; оно не является гарантией отсутствия ошибок.

### 14.5. Проверка качества кода Ruff

Storage Service:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\storage
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
```

API Gateway:

```powershell
cd C:\Users\admin\Downloads\lab5-microservices-manual\api-gateway
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
```

В итоговых проверках оба сервиса прошли `ruff check` и `ruff format --check`.

Если Ruff показывает, что файлы требуют форматирования, можно выполнить внутри соответствующего сервиса:

```powershell
.\.venv\Scripts\python.exe -m ruff format app tests
```

После этого повторите `ruff format --check`.

## 15. Возможные проблемы и решения

### Ошибка `No suitable Python runtime found`

Команда вида `py -3.12 -m venv .venv` не найдёт Python 3.12, если эта версия не зарегистрирована в Python Launcher.

Решение:

```powershell
py --list
py -3 --version
py -3 -m venv .venv
```

При выполненной работе `py -3` выбирал Python 3.14.3.

### Ошибка `...\ .venv\Scripts\python.exe` не распознана

Проверьте, что файл действительно существует:

```powershell
Test-Path .\.venv\Scripts\python.exe
Get-ChildItem .\.venv
```

Если внутри `.venv` есть `bin`, `include`, `lib`, но нет `Scripts`, окружение, вероятно, создавалось Unix-сборкой Python (например, MSYS). На проверочном компьютере именно это и произошло после `python -m venv .venv`.

Чтобы пересоздать **только повреждённое окружение конкретного сервиса** (из его папки), выполните:

```powershell
Remove-Item -Recurse -Force .venv
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Не удаляйте `.env` и `data/items.db`, если хотите сохранить настройки и товары.

### Ошибка при старте: отсутствуют обязательные настройки

Убедитесь, что `.env` существует в папке **каждого** микросервиса:

```powershell
Test-Path .env
Get-Content .env.example
```

Если `.env` отсутствует:

```powershell
Copy-Item .env.example .env
```

Не запускайте сервис из корня общего репозитория, если конфигурация и `run.py` рассчитаны на запуск из папки сервиса.

### API Gateway возвращает `503 Service Unavailable`

Проверьте, что Storage Service работает на порту `8001`, а адрес Storage Service в `api-gateway/.env` совпадает с ним. При остановленном Storage Service статус `503` является ожидаемым поведением, а не падением Gateway.

### В браузере виден `404 Not Found`

Если запрошены `/` или `/favicon.ico`, это допустимо. Для документации перейдите по адресу `http://127.0.0.1:8000/docs`. Для получения товара используйте путь `/items/{item_id}` с настоящим идентификатором.

### Порт `8000` или `8001` занят

Возможно, уже запущен другой экземпляр сервиса. Остановите прежний процесс `Ctrl + C` в соответствующем терминале. При изменении портов необходимо согласованно обновить `.env` обоих сервисов, чтобы Gateway обращался к правильному адресу Storage Service.

### PowerShell не разрешает `Activate.ps1`

Активация для этого проекта необязательна. Используйте команды вида:

```powershell
.\.venv\Scripts\python.exe run.py
.\.venv\Scripts\python.exe -m pytest tests -v
```

Если нужна именно активация окружения, изменение политики выполнения скриптов следует применять только при необходимости и с учётом правил безопасности системы.

## 16. Git и публикация проекта

Исходный код хранится в Git-репозитории на GitFlic:

https://gitflic.ru/project/lilrax/lab5-microservices-manual

Для проекта были созданы отдельные коммиты с настройками, реализацией Storage Service, реализацией API Gateway, тестами и документацией.

После редактирования `README.md` в **корне репозитория** можно выполнить:

```powershell
git status
git add README.md
git commit -m "docs: update Windows setup and run instructions"
git push origin main
```

Если команда `git status` выдаёт `fatal: not a git repository`, сначала перейдите в корень проекта, где находится каталог `.git`.

В `.gitignore` исключены локальные данные: виртуальные окружения `.venv`, файлы `.env`, базы SQLite `.db`, файлы покрытия и кэши. Шаблоны `.env.example` и `storage/data/.gitkeep` остаются в репозитории.

## 17. Результаты выполнения лабораторной работы

В ходе работы:

1. Разработаны два независимо запускаемых FastAPI-сервиса.
2. Реализовано синхронное взаимодействие по HTTP/JSON через `httpx`.
3. Реализованы создание и чтение товаров через API Gateway.
4. Данные сохраняются в SQLite на стороне Storage Service.
5. Выделены слои `api`, `domain`, `storage`, используются `Protocol` и внедрение зависимостей.
6. Конфигурация вынесена в `.env` и загружается через `pydantic-settings`.
7. Реализованы таймауты и контролируемая обработка сетевых ошибок (`503`, `502`).
8. Проверены успешные запросы `POST /items` (`201`) и `GET /items/1` (`200`).
9. Подтверждено восстановление доступа после перезапуска Storage Service (`200` → `503` → `200`).
10. Выполнены **18 тестов Storage Service** и **28 тестов API Gateway**; все успешно пройдены.
11. Достигнуто покрытие кода **99%** для Storage Service и **95%** для API Gateway.
12. Выполнены проверки Ruff, подготовлены `README.md` и `docs/architecture.md`, исходный код размещён на GitFlic.

## 18. Заключение

Лабораторная работа №5 демонстрирует создание микросервисной архитектуры на Python. В отличие от одного монолитного приложения система разделена на два процесса с собственными API, настройками и зонами ответственности.

API Gateway принимает внешние запросы и взаимодействует со Storage Service по HTTP, а Storage Service выполняет операции с данными и отвечает за их сохранение в SQLite. Такое разделение упрощает независимое тестирование компонентов и позволяет отдельно обрабатывать ошибки сетевого взаимодействия.

**Итог:** два микросервиса успешно запущены на Windows с Python 3.14.3, обмен данными работает, предусмотрена корректная обработка недоступности соседнего сервиса, все 46 тестов пройдены.



---

## Лабораторная работа №6 — Docker и Docker Compose

### Цель работы

Контейнеризировать два Python-микросервиса с помощью Docker
и организовать их совместный запуск через Docker Compose.

### Архитектура

В системе работают два микросервиса:

- **API Gateway** — принимает HTTP-запросы и обращается к Storage Service.
- **Storage Service** — работает с базой данных SQLite.

Сервисы обмениваются HTTP-запросами через внутреннюю сеть Docker.

### Используемые технологии

- Python 3.12
- FastAPI
- Docker
- Docker Compose
- SQLite
- Docker Volumes

### Запуск проекта

Для запуска необходим установленный и работающий Docker Desktop.

Откройте терминал в корневой папке проекта.

1. Создайте Docker volume для хранения базы данных:

   ```powershell
   docker volume create lab6-storage-data
   ```

2. Соберите образы и запустите микросервисы:

   ```powershell
   docker compose up --build -d
   ```

3. Проверьте состояние контейнеров:

   ```powershell
   docker compose ps
   ```

### Проверка работы

После запуска доступны:

- API Gateway: http://localhost:8080/docs
- Storage Service: http://localhost:8001/docs

Через API Gateway можно создать товар:

```json
{
  "name": "Mouse",
  "price": 750,
  "quantity": 3
}
```

Запрос: `POST http://localhost:8080/items`

Для получения созданного товара используется запрос:

`GET http://localhost:8080/items/{item_id}`

### Хранение данных

База данных SQLite хранится в Docker volume `lab6-storage-data`.

Данные сохраняются после остановки и пересоздания контейнеров.

### Остановка проекта

```powershell
docker compose down
```

Команда останавливает и удаляет контейнеры, но сохраняет базу данных
в Docker volume.

Для повторного запуска используйте:

```powershell
docker compose up -d
```
