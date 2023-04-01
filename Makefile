celery:
	celery -A main.celery worker --loglevel=info
flower:
	celery -A main.celery flower --port=5555
