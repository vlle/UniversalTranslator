## Переводчик с любого на любой язык

- Даже с собачьего на рыбий.

## Стек

- Python3.10, async SQLAlchemy, FastAPI, Docker, Docker-compose, PostgreSQL, psycopg3, pre-commit hooks, OpenAI API.
- Линтеры: black, isort
- Настроен GitHub Workflow

## Фичи
- CRUD интерфейс
- Возможность переводить с любого языка на любой. Вообще.
- Сохранение всех языков (с которого переводят, на который переводят)
- Тестирование через pytest
- Докер-компоуз с постгрей

## Как задеплоить

- Заполните API_KEY в env.example своим ключом OpenAI API.

- ```cp env.example app/.env ```
- ```docker-compose up --build -d ```

## Как тестировать
Загитклоньте проект, и находясь на одном уровнем с папкой app:
``` pytest app/ -v ```

## Примеры запросов:

```bash
curl -X POST "http://localhost:8000/api/v1/create_language" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "English"
  }'
  ```

```bash
curl -X POST "http://localhost:8000/api/v1/create_translation" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello",
    "translate_to_language": "French"
  }'
  ```


```bash
curl -X GET "http://localhost:8000/api/v1/get_language?name=English"
```




## Демо

- Видео: [![asciicast](https://asciinema.org/a/uHUhxR2IgNQwKERDord4cgd6g.svg)](https://asciinema.org/a/uHUhxR2IgNQwKERDord4cgd6g)
- Задеплоено в https://vlle.ru/api/v1/ (отключено https://vle.ru/docs)
