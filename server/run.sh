# You should use it in a screen.. 
# Starting Gunicorn

# only if not started before
#sudo service rabbitmq-server start
#sudo service nginx start
#python manage.py run_gunicorn

gunicorn server.wsgi:application --bind 127.0.0.1:8000 --log-file /var/log/www/heimdall.gunicorn.log --log-level debug
