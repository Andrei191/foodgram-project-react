[![Django-app workflow](https://github.com/Andrei191/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Andrei191/foodgram-project-react/actions/workflows/main.yml)

### Foodgram - сайт с рецептами

#### Foodgram - сервис для публикации рецептов. Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты в избранное, в покупки, скачать список покупок. Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других авторов

#### стек технологий: python3, Django Rest Framework, PostgreSQL,  Docker, gunicorn, nginx, Яндекс.Облако Ubuntu 20.04

##### Подготовка и запуск проекта

Склонировать репозиторий на локальную машину:

```
git clone https://github.com/Andrei191/foodgram-project-react
```

#### Выполните вход на свой удаленный сервер

#### Установите docker на сервер

```
sudo apt install docker.io 
```

#### Установите docker-compose на сервер(актуальная версия [тут](https://github.com/docker/compose/releases))

```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

#### Затем необходимо задать правильные разрешения, чтобы сделать команду docker-compose исполняемой

```
sudo chmod +x /usr/local/bin/docker-compose
```

#### Скопируйте файлы docker-compose.yml и nginx.conf из проекта на сервер

```
scp docker-compose.yaml <username>@<host>:/home/<username>/docker-compose.yaml
```

```
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

#### Добавьте в Secrets GitHub переменные окружения для работы

```
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PASSWORD=admin
DB_PORT=5432
DB_USER=postgres

DOCKER_PASSWORD=<Docker password>
DOCKER_USERNAME=<Docker username>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ(cat ~/.ssh/id_rsa)>

TG_CHAT_ID=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```

#### Запушить на Github. После успешного деплоя зайдите на боевой сервер и выполните команды

#### Собрать статические файлы в STATIC_ROOT

```
docker-compose exec backend python3 manage.py collectstatic --noinput
```

#### Применить миграции

```
docker-compose exec backend python3 manage.py migrate --noinput
```

#### Загрузите ингридиенты в базу данных

```
sudo docker-compose exec backend python manage.py fill_db
```

#### Создать суперпользователя Django

```
docker-compose exec backend python manage.py createsuperuser
```

#### Образы на DockerHub: [бекенд](https://hub.docker.com/repository/docker/andrei191000/foodgram_backend), [фронтенд](https://hub.docker.com/repository/docker/andrei191000/foodgram_frontend)

---

#### Данный проект доступен по [ссылке](http://84.201.138.122/)

---

#### Вход в админку

login:

```
admin
```

password:

```
admin
```

---

Автор: [Карасев Андрей](https://github.com/Andrei191/)
