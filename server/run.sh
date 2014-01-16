# You should use it in a screen.. 
# Starting Gunicorn
sudo service rabbitmq-server start
sudo service nginx start
python manage.py run_gunicorn