#!/bin/bash
echo "Aguardando MySQL..."
sleep 5

echo "Aplicando makemigrations"
python manage.py makemigrations --noinput

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn ong_sol.wsgi:application --config docker/gunicorn.conf.py

