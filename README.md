# Проектная работа 7 спринта

Упростите регистрацию и аутентификацию пользователей в Auth-сервисе, добавив вход через социальные сервисы. Список сервисов выбирайте исходя из целевой аудитории онлайн-кинотеатра — подумайте, какими социальными сервисами они пользуются. Например, использовать [OAuth от Github](https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps){target="_blank"} — не самая удачная идея. Ваши пользователи не разработчики и вряд ли имеют аккаунт на Github. А вот добавить Twitter, Facebook, VK, Google, Yandex или Mail будет хорошей идеей.

Вам не нужно делать фронтенд в этой задаче и реализовывать собственный сервер OAuth. Нужно реализовать протокол со стороны потребителя.

Информация по OAuth у разных поставщиков данных: 

- [Twitter](https://developer.twitter.com/en/docs/authentication/overview){target="_blank"},
- [Facebook](https://developers.facebook.com/docs/facebook-login/){target="_blank"},
- [VK](https://vk.com/dev/access_token){target="_blank"},
- [Google](https://developers.google.com/identity/protocols/oauth2){target="_blank"},
- [Yandex](https://yandex.ru/dev/oauth/?turbo=true){target="_blank"},
- [Mail](https://api.mail.ru/docs/guides/oauth/){target="_blank"}.

## Дополнительное задание

Реализуйте возможность открепить аккаунт в соцсети от личного кабинета. 

Решение залейте в репозиторий текущего спринта и отправьте на ревью.

















# Project

Project contains 2 services:
* **Application API** - API for movies, persons and genres
* **Authentication** - Authentication service 

## Base commands
 - `make run_app` - run the application and auth service
 - `make run_sample_app` - run the application and auth service with sample env variables
 - `make run_tests` - run tests for authentication service
 - `make down` - stop and remove containers, networks, volumes, and images with --remove-orphans flag
 - `make init_db` - initialize database, create and apply first migration
 - `make db_upgrade` - apply existing migrations
 - `make create_superuser` - create user with access to every authentication service resource

## Get started
To use authentication service you need:
 - run the auth container:
   - if you have the environment file *.env* use `make run_app`
   - if you want to run test version of auth service use `make run_sample_app`
 - initialize database:
   - if you want to start from scratch:
     - make sure that you don't have migration folder (*auth/migrations*)
     - run `make init_db`
     - it's recommended to rename the migration file and the revision number for better user experience. 
     
        For example: *0001_initial_migration.py* and revision number *0001*
   - if you want to use existing migrations use `make db_upgrade`
 - you can create superuser to have access to all authentication endpoints using `make create_superuser`

## Application API
### Description
API service provides access to all movies, persons and genres information.
Films and persons are searchable by title, description and full name respectively.
Pagination and cache are implemented for a better user experience

### Swagger documentation
More detailed information about service's endpoints is available 
[here](http://0.0.0.0:80/api/openapi) after project start (`make run_app`)


## Authentication service
### Description
Service implements API for authentication and user profile 
and admin API for operating role management system.
Authentication is based on access and refresh JWT tokens.
Access token is stored in 'Authorization' header and refresh token - in HttpOnly cookie

### Swagger documentation
More detailed information about service's endpoints is available 
[here](http://0.0.0.0:80/swagger/ui) after project start (`make run_app`)


**_Link to GitHub_**: `https://github.com/IRepeva/Auth_sprint_1`


