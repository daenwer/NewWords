redis-server --port 6370

venv/bin/python -m celery -A NewWords worker -n words -Q words --loglevel=debug --concurrency=4

не используется
celery -A NewWords beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

gunicorn --bind 0.0.0.0:8000 NewWords.wsgi


python3 -m celery -A NewWords worker -n words -Q words --loglevel=debug --concurrency=1

cp /root/NewWords/configs/prod.conf /etc/supervisor/conf.d/prod.conf

supervisorctl reread
supervisorctl update
