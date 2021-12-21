# Django Rest API Boilerplate

## Technology used
1. Python3.8
2. Django 3
3. Django Rest Framework
4. MySql
5. Docker

## Features
* User SignIn/SignUp
* Forget Password
* Email Verification
* Login with Social Accounts (Facebook/Google)
* OAuth 2.0 (Authentication with Access & Refresh Token)
* Swagger Documentation
* Testing - [**Coming Soon**]
* Docker Config - [**Coming Soon**]

## Setup in your local machine
1. Clone project
```
git clone https://github.com/morshedmasud/django-rest-framework-mysql-boilerplate
```
2. Go to project root path and create virtualenv
```
virtualenv -p python3 venv
```
3. Active virtualenv
```
source venv/bin/activate
```
4. Install all dependency
```shell script
pip3 install -r requirements.txt
```
5. Don't forget to create **.env** file as like **.env.example** and put necessary values like **DB Info, Email Info**
6. Database migrations
```shell script
python3 manage.py makemigrations
```
7. Database Migrate
```shell script
python3 manage.py migrate
```
8. Database Migrate and Seeder
```shell script
bash migrate_and_seed.sh
```
9. Finally, run the project by 
```shell script
python3 manage.py runserver
```
10. Generated staticfiles 
```shell script
python3 manage.py collectstatic
``` 

#### Open the following url for view swagger documentation
## (http://localhost:8000/swagger/)
