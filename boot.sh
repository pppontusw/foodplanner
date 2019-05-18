#!/bin/sh
source venv/bin/activate
while true; do
   alembic upgrade head
   if [[ "$?" == "0" ]]; then
       break
   fi
   echo Upgrade command failed, retrying in 5 secs...
   sleep 5
done
exec gunicorn -b :5000 --access-logfile - --error-logfile - weathercentral:app