#!/bin/bash
source env/bin/activate
export DATABASE_URL="postgresql://localhost/kenddic"

export FLASK_APP=app.py
export FLASK_ENV=development
#flask run
#gunicorn -b 127.0.0.1:8080 app:app 
gunicorn -b 0.0.0.0:8080 app:app
