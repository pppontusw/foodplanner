# foodplanner-api

[![Build Status](https://travis-ci.org/pppontusw/foodplanner-api.svg?branch=master)](https://travis-ci.org/pppontusw/foodplanner-api)
[![codecov](https://codecov.io/gh/pppontusw/foodplanner-api/branch/master/graph/badge.svg)](https://codecov.io/gh/pppontusw/foodplanner-api)

Flask backend API for the foodplanner application

Environment variables available for configuration:

```env
MAIL_USERNAME="noreply@yourdomain.com"
MAIL_PASSWORD="smtp_password"
MAIL_SERVER="smtp.yourdomain.com"
MAIL_DEFAULT_SENDER="noreply@yourdomain.com"
DATABASE_URL="postgresql://pg_user:pg_password@pg_host/pg_database"
SECRET_KEY="randomsecretkey"
SECURITY_PASSWORD_SALT="randomsalt"
```

note: DATABASE_URL can be left out if you want to use a SQLite database, but this isn't recommended - because we don't support cascading deletes in SQLite so you will end up with orphans in your database when deleting their parents.

1. Install requirements with `pip install -r requirements.txt`

2. Run database migration with `alembic upgrade head`

3. Run the application with `python foodlist.py`, or build it using the Dockerfile.

## TESTING

### UNIT TESTS

`python -m unittest discover tests/ -v`

### CODE COVERAGE

`coverage run -m unittest discover tests/`

To create a nice html report run `coverage html`
