# Adaptive Learning Toolbox

### Дополнительные инструменты

1. Инструмент анализа качества тестовых материалов - https://github.com/dim3662/ColibrateWithLti
2. Инструмент построения компетентностной модели курса
3. Визуализатор образовательных достижений


### Настройка Moodle Provider

https://youtube.com/playlist?list=PLYDrQMWz8b9UvvjgTuHHDqwZ4s0ajU617

1. Запустить в Docker контейнеры moodle и maria db
2. Создать курс и пробный тест
3. Настроить Lti Plugin
    + Site Administration 🡒 Plugins 🡒 Authentication 🡒 Manage Authentication 🡒 LTI  
    + Site Administration 🡒 Plugins 🡒 Enrolments 🡒 Manage Enrol Plugins 🡒 Publish as LTI tool
    + Site Administration 🡒 Security 🡒 HTTP Security 🡒 Allow frame embedding
4. Опубликовать пробный тест через Publish as LTI tool
5. Настроить Web Services
    + Site Administration 🡒 Plugins 🡒 Web Services 🡒 Enable web services
    + Site Administration 🡒 Plugins 🡒 Web Services 🡒 Enable protocols 🡒 REST
    + Site Administration 🡒 Plugins 🡒 Web Services 🡒 Select service 🡒 Add (НЕ ЗАБЫТЬ ПОСТАВИТЬ ГАЛОЧКУ Enabled)
    + Site Administration 🡒 Plugins 🡒 Web Services 🡒 Add functions
        ```
        mod_quiz_get_user_best_grade
        mod_quiz_get_user_attempts
        mod_quiz_get_quizzes_by_courses
        core_user_get_users
        ```
    + Site Administration 🡒 Plugins 🡒 Web Services 🡒 Manage tokens 🡒 Add 🡒 Admin\LtiService

### Запуск

```
python manage.py migrate &&
gunicorn --certfile=/config/config/certs/localhost.crt --keyfile=/config/config/certs/localhost.key ltibridge.wsgi:application --bind 0.0.0.0:443
```

### Деплой

Локально

* docker build -t romankalganov1/lti-bridge .
* docker push romankalganov1/lti-bridge

На сервере

* docker pull romankalganov1/lti-bridge
* docker-compose kill web
* docker-compose rm web
* docker-compose up -d


### TODO

1. Сделать правильную организацию пакетов\модулей
2. Сделать фильтрацию на базе, при невозможности сделать при помощи py2neo отказаться от него
3. Написать тесты
4. Сделать видео про IRT 
5. Привести в порядок settings.py
6. Синхронизация пользователей в графе и мудле
