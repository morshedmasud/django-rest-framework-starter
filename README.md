# Django Rest API Boilerplate

## Technology used
1. Python3.8
2. Django 3
3. Django Rest Framework
4. MySql
5. Docker

## Features
* User SignIn/SignUp
* Login with Social Accounts (Facebook/Google) - Coming Soon
* OAuth 2.0
* Swagger Documentation
* Testing - Coming Soon
* Docker Config - Coming Soon

## Setup in your local machine
1. Clone project
```
git clone https://github.com/morshedmasud/django-rest-framework-mysql-boilerplate
```
2. Create virtualenv
```
virtualenv -p python3 venv
```
3. Active virtualenv
```
. venv/bin/activate
```
4. Go to project root path and install all dependency
```shell script
pip3 install -r requirements.txt
```
5. Database migrations
```shell script
python3 manage.py makemigrations
```

6. Database Migrate
```shell script
python3 manage.py migrate
```

7. Database Migrate and Seeder
```shell script
bash migrate_and_seed.sh
```

6. Finally run the project by 
```shell script
python3 manage.py runserver
```
7. Generated staticfiles 
```shell script
python3 manage.py collectstatic
``` 

#### Open the following url for view swagger documentation
## [swagger-docs](http://localhost:8000/swagger/)
