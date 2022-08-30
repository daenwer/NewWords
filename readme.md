redis-server --port 6370

venv/bin/python -m celery -A NewWords worker -n words -Q words --loglevel=debug --concurrency=4