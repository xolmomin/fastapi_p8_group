celery:
	celery -A main.celery worker --loglevel=info
flower:
	celery -A main.celery flower --port=5555

rabbitmq:
	docker run -p 15672:15672 -p 5672:5672 rabbitmq:3-management