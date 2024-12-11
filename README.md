# GitHub Top100 API

Это RESTful API на базе **FastAPI** для отображения топ-100 репозиториев GitHub и статистики их коммит-активности. В проекте предусмотрена периодическая загрузка данных из GitHub в PostgreSQL. Также есть возможность развёртывания в Docker и интеграции с Яндекс.Облаком (в том числе через Cloud Functions для периодического парсинга данных).

## Основные возможности

- **GET** `/api/v1/repos/top100` – Получение топ-100 публичных репозиториев по количеству звёзд с возможностью сортировки по разным полям (звёзды, форки и т.д.).
- **GET** `/api/v1/repos/{owner}/{repo}/activity?since=YYYY-MM-DD&until=YYYY-MM-DD` – Получение информации о ежедневной коммит-активности (количество коммитов и авторы) за указанный промежуток.

## Стек технологий

- **Язык**: Python 3.11+  
- **Фреймворк**: FastAPI (для RESTful API)  
- **База данных**: PostgreSQL  
- **Библиотека для работы с БД**: asyncpg (чистый SQL, без ORM)  
- **Контейнеризация**: Docker + Docker Compose  
- **Инфраструктура (опционально)**: Yandex Cloud (Compute VM, Managed PostgreSQL, Serverless Containers, Cloud Functions)  
- **Документация API**: Swagger UI (доступна по `/docs`)

## Функции для локального развёртывания

1. Клонирование репозитория:
   ```bash
   git clone https://github.com/MamontovAndrew/ecometio_test.git
   cd <your_repo>
   ```

2. Настройка окружения:  
   Создайте файл `.env` в корне проекта:
   ```env
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   POSTGRES_USER=myuser
   POSTGRES_PASSWORD=mypassword
   POSTGRES_DB=mydb
   GITHUB_TOKEN=XXXXXXXXXXXX
   ```

3. Создание таблиц в БД:  
   Запустите сначала контейнер с БД:
   ```bash
   docker compose up -d db
   ```
   Затем подключитесь к базе:
   ```bash
   docker exec -it postgres_db psql -U myuser -d mydb
   ```
   
   Выполните в psql:
   ```sql
   CREATE TABLE IF NOT EXISTS top100 (
       repo TEXT NOT NULL,
       owner TEXT NOT NULL,
       position_cur INT NOT NULL,
       position_prev INT,
       stars INT NOT NULL,
       watchers INT NOT NULL,
       forks INT NOT NULL,
       open_issues INT NOT NULL,
       language TEXT,
       PRIMARY KEY (owner, repo)
   );

   CREATE TABLE IF NOT EXISTS activity (
       owner TEXT NOT NULL,
       repo TEXT NOT NULL,
       date DATE NOT NULL,
       commits INT NOT NULL,
       authors TEXT[] NOT NULL,
       PRIMARY KEY (owner, repo, date)
   );
   ```
   
   Выйдите из psql командой `\q`.

4. Запуск приложения:
   ```bash
   docker compose up --build
   ```
   
   Приложение будет доступно по адресу:  
   [http://localhost:8000](http://localhost:8000)

5. Документация:
   [http://localhost:8000/docs](http://localhost:8000/docs)

Если таблицы не существуют, приложение при старте выдаст ошибку. Если таблицы пусты, эндпоинты вернут пустой массив.

## Структура репозитория

```
.
├── app
│   ├── main.py
│   ├── api
│   │   ├── v1
│   │   │   ├── endpoints
│   │   │   │   ├── repos.py
│   │   │   │   └── activity.py
│   │   │   ├── __init__.py
│   │   └── __init__.py
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── crud
│   │   ├── repos.py
│   │   └── activity.py
│   ├── schemas
│   │   ├── repos.py
│   │   └── activity.py
│   ├── dependencies.py
│   ├── utils
│   │   ├── github_api.py
│   │   └── __init__.py
│   ├── logging_config.py
│   └── __init__.py
├── parser
│   ├── parse_repos.py
│   ├── requirements.txt
│   └── deploy.sh
├── docker compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

## Работа с API

Примеры запросов:

- Получение топ 100 репозиториев:
  ```bash
  curl "http://localhost:8000/api/v1/repos/top100"
  ```
  
  С параметрами сортировки:
  ```bash
  curl "http://localhost:8000/api/v1/repos/top100?sort_by=stars&order=desc"
  ```

- Получение активности репозитория:
  ```bash
  curl "http://localhost:8000/api/v1/repos/owner_name/repo_name/activity?since=2024-12-01&until=2024-12-10"
  ```

## Периодическое обновление данных (Парсер)

В папке `parser` находится скрипт `parse_repos.py`. Его можно развернуть в Яндекс.Облаке как Cloud Function и настроить крон-триггер для периодического запуска. Этот скрипт будет обновлять таблицы `top100` и `activity` данными из GitHub.

- Собрать ZIP архив со скриптом и зависимостями.
- Деплой в Yandex Cloud Function через `yc` CLI или Terraform.
- Установить переменные окружения (POSTGRES_HOST, POSTGRES_USER и т.д.) для функции.
- Создать триггер по расписанию для автоматического обновления данных.

## Развёртывание в Яндекс.Облаке

- **Compute Cloud (ВМ)**: Разверните ВМ, установите Docker, загрузите проект и выполните локальные инструкции.
- **Managed Kubernetes**: Опубликуйте Docker-образ в Yandex Container Registry, создайте Deployment/Service/Ingress манифесты и задеплойте их.
- **Serverless Containers**: Опубликуйте образ и создайте Serverless Container, настроив переменные окружения.


1. **Сборка ZIP-архива для Cloud Function**  
   В папке `parser` выполните скрипт `deploy.sh`:
   ```bash
   cd parser
   sh deploy.sh
   ```

   Этот скрипт:
   - Устанавливает зависимости в папку `deps`.
   - Создаёт архив `function.zip`, включающий скрипт `parse_repos.py` и зависимости.

2. **Создание бакета для Object Storage**
   Если бакет ещё не создан, создайте его:
   ```bash
   yc storage bucket create --name github-parser-bucket-no-limit
   ```

3. **Загрузка ZIP-архива в Object Storage**
   Используйте AWS CLI для загрузки архива в бакет:
   ```bash
   aws --endpoint-url=https://storage.yandexcloud.net s3 cp ./parser/function.zip s3://github-parser-bucket-no-limit/
   ```

4. **Создание Cloud Function**
   Создайте версию функции с использованием архива из Object Storage:
   ```bash
   yc serverless function version create \
     --function-name github-parser \
     --runtime python311 \
     --entrypoint parse_repos.handler \
     --memory 128m \
     --execution-timeout 300s \
     --source-path "s3://github-parser-bucket-no-limit/function.zip" \
     --environment POSTGRES_HOST="host" \
     --environment POSTGRES_PORT="5432" \
     --environment POSTGRES_USER="user" \
     --environment POSTGRES_PASSWORD="pass" \
     --environment POSTGRES_DB="db" \
     --environment GITHUB_TOKEN="github_pat_xxxxx" \
     --service-account-id <SERVICE_ACCOUNT_ID>
   ```

5. **Создание крон-триггера для периодического вызова функции**
   Настройте автоматический вызов функции:
   ```bash
   yc serverless trigger create timer \
     --name github-parser-cron \
     --cron-expression "0 0 * * ? *" \
     --invoke-function-name github-parser
   ```

### Ручной вызов Cloud Function

Для тестирования вызовите функцию вручную:
```bash
yc serverless function invoke --name github-parser
```

### Проверка работы

- **Логи функции**:
  ```bash
  yc logging read --log-group-name=serverless-function --function-name=github-parser --lines 100
  ```

- **Проверка доступа к объекту**:
  ```bash
  aws --endpoint-url=https://storage.yandexcloud.net s3 ls s3://github-parser-bucket-no-limit/
  ```

### Роли и доступы

Убедитесь, что сервисный аккаунт имеет необходимые права:
```bash
yc resource-manager folder add-access-binding \
  --id <FOLDER_ID> \
  --role storage.viewer \
  --service-account-id <SERVICE_ACCOUNT_ID>
```

Также проверьте, что Cloud Function может читать объект:
```bash
aws --endpoint-url=https://storage.yandexcloud.net s3api put-object-acl \
  --bucket github-parser-bucket-no-limit \
  --key function.zip \
  --acl public-read
```

## Дополнительная информация

- Если таблицы не созданы – приложение выкинет исключение при старте.
- Если таблицы пусты – запросы вернут пустые массивы.
- Логи приложения можно просмотреть командой:
  ```bash
  docker compose logs
  ```
- Документация (Swagger UI) доступна по адресу:  
  [http://localhost:8000/docs](http://localhost:8000/docs)
