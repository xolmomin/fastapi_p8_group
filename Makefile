mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

celery:
	docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management
	celery -A main.celery worker --loglevel=info
	celery -A main.celery flower --port=5555
