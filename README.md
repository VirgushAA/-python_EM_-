## Backend-сервис на FastAPI с JWT-аутентификацией и ролевой моделью доступа (RBAC). Проект демонстрирует архитектуру API и механизмы авторизации.

## Authentication

- Регистрация и логин по email + пароль
- Пароли хранятся в виде bcrypt-хэша
- После логина выдаётся JWT access token
- Токен передаётся в заголовке: Authorization: Bearer <token>
- JWT содержит:
- - sub — ID пользователя
- - exp — время истечения токена
- Обработка ошибок JWT
- - Просроченный токен → 401 Token expired
- - Некорректный токен → 401 Invalid token
- - Неактивный пользователь → 401 User inactive

## Authorization

### Используется Role-Based Access Control:

- Пользователь может иметь несколько ролей
- Роль содержит набор разрешений
- Разрешение описывается строкой вида: resource.action[.scope]"
- Примеры:
- - post.read
- - post.create
- - post.update.own
- - comment.delete

### Проверка прав

- Проверка роли:
- - Depends(require_role("admin"))
- Проверка разрешения:
- - Depends(require_permission("post.create"))

*Проверка выполняется на уровне dependency, до входа в обработчик.*


## Роли и права (seed)

Предустановленные роли:
- admin
- - полный доступ ко всем ресурсам и действиям

- moderator
- - управление постами и комментариями

- user
- - создание и управление своими ресурсами

- auditor
- - доступ только на чтение

- guest

- - минимальный read-only доступ

При инициализации БД автоматически создаются тестовые пользователи:

- admin@mail.ru     / password
- moderator@mail.ru / password
- user@mail.ru      / password
- auditor@mail.ru   / password
- guest@mail.ru     / password


### Мок-эндпоинты ресурсов

Реализованы демонстрационные эндпоинты:

- /post
- /users
- /me
- /auth

Они используются только для проверки:

- JWT
- ролей
- разрешений
- активности пользователя

*Фактической бизнес-логики (БД постов, комментариев и т.д.) нет.*

### База данных

По умолчанию используется SQLite

ORM: SQLAlchemy

Архитектура позволяет без изменений кода перейти на PostgreSQL

Смена БД не должна повлиять на слой авторизации.


## Запуск проекта
### Запуск сервера

- uvicorn main:app --reload
- Документация Swagger
- - http://127.0.0.1:8000/docs

### Экстренная остановка
- Windows
- - taskkill /IM python.exe /F
- - taskkill /IM uvicorn.exe /F
- linux
- - pkill -f uvicorn
- - pkill -f python

## Установка зависимостей

Создать виртуальное окружение и установить пакеты:

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Примечания

Logout реализуется на стороне клиента (удаление токена)

Все проверки выполняются синхронно через FastAPI dependencies

База данных app.db уже инициализирована с ролями,
правами и тестовыми пользователями.
Чтобы начать с инициализации чистой базы, можно удалить файл
и перезапустите сервер.
