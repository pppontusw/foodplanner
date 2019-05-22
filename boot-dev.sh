#!/bin/sh
source /venv/bin/activate
while true; do
   alembic upgrade head
   if [[ "$?" == "0" ]]; then
       break
   fi
   echo Upgrade command failed, retrying in 5 secs...
   sleep 5
done
export FLASK_DEBUG=True
exec flask run --host=0.0.0.0