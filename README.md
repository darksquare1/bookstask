
## Описание
Система для управления книгами, авторами, читателями и процессом выдачи книг. Включает регистрацию и аутентификацию с JWT, разделение на роли (админ и читатель). 

Админ может управлять жанрами, книгами, авторами. А так же он может изымать книги у пользователей.
Читатель — может смотреть список существующих авторов, жанров, книг, а так же брать и возвращать доступные книги.

Каждый ендпоинт требует авторизацию, для этого требуется зарегистрироваться, затем залогиниться, после этого будет выдан токен доступа.
Токен доступа передается в заголовках запроса как "Authorization: bearer сам токен"
## Запуск проекта
Создайте .env файл
```
DB_HOST='db'
DB_PORT='5432'
DB_USER='changeme'
DB_PASS='changeme'
DB_NAME='changeme'
SECRET_KEY='changeme'
ALGORITHM='changeme'
ACCESS_TOKEN_EXPIRE_MINUTES=changeme
DB_TEST_NAME='changeme'
```
ALGORITHM и SECRET_KEY это переменные, нужные для шифрования и дешифрования токена.
ACCESS_TOKEN_EXPIRE_MINUTES - количество времени в минутах, в течение которого можно авторизовываться по выданному при логине токену.

Для сборки и запуска всех контейнеров используйте команду:

```bash
docker-compose up -d --build
```
## Запуск тестов
```bash
docker exec -it books_task_postgres psql -U postgres -h db -c "CREATE DATABASE testdb;"
```
Вместо postgres и testdb укажите свои названия из переменных окружения, далее введите пароль для вашего пользователя бд.
Как только база данных создана, можете запустить тесты командой:
```bash
docker exec -it books_task_app pytest tests
```
## Наполнение таблиц
Если хотите наполнить таблицы пользователями, книгами и авторами, введите
```bash
docker exec -it books_task_app python app/db/fixtures.py
```
Админ будет доступен по username: admin, password: hashedpassword
## Документация
После запуска контейнеров документация будет доступна по адресу: http://127.0.0.1:8000/docs