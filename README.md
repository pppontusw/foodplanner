# foodplanner

[![Build Status](https://travis-ci.org/pppontusw/foodplanner.svg?branch=master)](https://travis-ci.org/pppontusw/foodplanner)

Flask application to store and create weekly food lists

1. Following env variables are used for configuration and should be specified;

```
MAIL_USERNAME="noreply@yourdomain.com"
MAIL_PASSWORD="smtp_password"
MAIL_SERVER="smtp.yourdomain.com"
MAIL_DEFAULT_SENDER="noreply@yourdomain.com"
DATABASE_URL="postgresql://pg_user:pg_password@pg_host/pg_database"
SECRET_KEY="randomsecretkey"
SECURITY_PASSWORD_SALT="randomsalt"
```
note: DATABASE_URL can be left out if you want to use a SQLite database

and you need to configure alembic.ini with your DATABASE_URL (they should be identical)

2. Install requirements with `pip install -r requirements.txt`

3. Run database migration with `alembic upgrade head`

4. Run the application with `python foodlist.py`, or build it using the Dockerfile 

Note: if you build a Docker image from the default Dockerfile, you need a similar .env-prod and alembic-prod.ini with database and mail configuration for your production env. A similar setup exists for the Docker-compose and Dockerfile-dev, if you want to develop in Docker live.
