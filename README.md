# foodplanner-api

[![Build Status](https://travis-ci.org/pppontusw/foodplanner.svg?branch=master)](https://travis-ci.org/pppontusw/foodplanner)

Flask backend API for the foodplanner application

Environment variables available for configuration:

```
MAIL_USERNAME="noreply@yourdomain.com"
MAIL_PASSWORD="smtp_password"
MAIL_SERVER="smtp.yourdomain.com"
MAIL_DEFAULT_SENDER="noreply@yourdomain.com"
DATABASE_URL="postgresql://pg_user:pg_password@pg_host/pg_database"
SECRET_KEY="randomsecretkey"
SECURITY_PASSWORD_SALT="randomsalt"
```

note: DATABASE_URL can be left out if you want to use a SQLite database, but this isn't recommended.

1. Install requirements with `pip install -r requirements.txt`

2. Run database migration with `alembic upgrade head`

3. Run the application with `python foodlist.py`, or build it using the Dockerfile.
