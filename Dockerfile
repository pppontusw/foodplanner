FROM python:3.7-alpine

RUN adduser -D foodlist

WORKDIR /home/foodlist

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apk add --update gcc build-base postgresql-dev python3-dev musl-dev
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install psycopg2-binary

COPY alembic alembic
COPY app app
COPY .env-prod .env
COPY alembic-prod.ini alembic.ini
COPY foodlist.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP foodlist.py

RUN chown -R foodlist:foodlist ./
USER foodlist

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]