# Социальная сеть Yatube

## Описание
Социальная сеть, где пользователи могут оставлять свои посты на разные темы, комментировать чужие, а также подписываться на интересных авторов.

## Стек
Python3, Django 2.2, PostgreSQL

## Команды для запуска приложения
- Склонируйте репозиторий к себе на компьютер и разверните виртуальное окружение<br>
```python -m venv venv```
- Затем установите зависимости<br>
```pip install -r requirements.txt```

Для дальнейшей работы понадобиться PostgreSQL.

### Настройка PostgreSQL
- Из консоли PostgreSQL создаем и настраиваем пользователя при помощи которого будем соединяться с базой данных из Django
```
create user <ваш username> with password <ваш пароль>;
alter role <ваш username> set client_encoding to 'utf8';
alter role <ваш username> set default_transaction_isolation to 'read committed';
alter role <ваш username> set timezone to 'UTC';
```
- Создаем базу проекта<br>
```create database <имя базы> owner <ваш username>;```

Далее нужно выйти из консоли PostgreSQL
- В корневой дирректории проекта создаем файл .env и прописываем внутри него:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы>
DB_USER=<ваш username>
DB_PASSWORD=<ваш пароль>
DB_HOST='127.0.0.1'
DB_PORT=5432
SECRET_KEY=<ваш django_secret_key>
```
что бы сгенерировать SECRET_KEY нужно из корневой дирректории выполнить:
```python manage.py shell```

Затем:
```
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Cкопировать полученный ключ в .env

Выполняем миграции и собираем статику<br>
```python manage.py migrate```<br>
```python manage.py collectstatic```


## Заполнение базы начальными данными
Для заполнения базы начальными данными выполните команду.<br>
```python manage.py loaddata init_data.json```

## Команда для содания суперпользователя
Для создание суперпользователя выполните команду:<br>
```python manage.py createsuperuser```<br>

## Основные возможности
Регистрация и вход в учетную запись по имени пользователя и паролю.<br>
Создание новых постов для зарегистрированных пользователей(возможность выбрать определенную тему/группу, прикрепить картинку)<br>
Редактирование собственных постов<br>
Просмотр постов, созданных другими пользователями<br>
Просмотр постов определенного автора или постов на определенную тему<br>
Комментирование постов для зарегистрированных пользователей<br>
Подписка(отписка) на интересных авторов и просмотр только избранных авторов для зарегистрированных пользователей<br>
Просмотр списка тем/групп<br>

## Контакты
Email: ikonstantin1991@mail.ru<br>
Telegram: @ikonstantin91
