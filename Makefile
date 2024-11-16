APP_CONTAINER = app
DJANGO_CMD = docker compose exec $(APP_CONTAINER) bash -c "python manage.py"
DOCKER_RUN = docker compose run --rm $(APP_CONTAINER)

run:
	@echo "Starting the application..."
	docker compose up

install: migrations migrate superuser
	@echo "Installation completed."

migrations:
	@echo "Making migrations..."
	$(DJANGO_CMD) makemigrations

migrate:
	@echo "Applying migrations..."
	$(DJANGO_CMD) migrate

superuser:
	@echo "Creating superuser..."
	$(DJANGO_CMD) createsuperuser

shell:
	@echo "Starting Django shell..."
	docker compose run --rm $(APP_CONTAINER) shell

lint:
	@echo "Running linter (ruff)..."
	docker compose run --rm $(APP_CONTAINER) ruff check --fix

test:
	@echo "Running tests..."
	docker compose run --rm $(APP_CONTAINER) pytest -svv
