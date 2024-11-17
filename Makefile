APP_CONTAINER = app
DOCKER_RUN = docker compose run --rm $(APP_CONTAINER)
DJANGO_CMD = $(DOCKER_RUN) bash -c "python manage.py"
WAIT_FOR_IT = ./docker/wait-for-it.sh

# Start the application
run:
	@echo "Starting the application..."
	docker compose up --build

# Install the application (migrations, superuser, etc.)
install: wait-services migrations migrate superuser
	@echo "Installation completed."

# Wait for all services to be ready
wait-services:
	@echo "Waiting for dependent services..."
	$(WAIT_FOR_IT) db:5432 -- echo "Postgres is ready"
	$(WAIT_FOR_IT) redis:6379 -- echo "Redis is ready"
	$(WAIT_FOR_IT) clickhouse:8123 -- echo "ClickHouse is ready"

# Apply database migrations
migrations:
	@echo "Making migrations..."
	$(DJANGO_CMD) makemigrations

migrate:
	@echo "Applying migrations..."
	$(DJANGO_CMD) migrate

# Create a superuser
superuser:
	@echo "Creating superuser..."
	$(DJANGO_CMD) createsuperuser

# Start a Django shell
shell:
	@echo "Starting Django shell..."
	$(DOCKER_RUN) bash -c "python manage.py shell"

# Run linter (ruff)
lint:
	@echo "Running linter (ruff)..."
	$(DOCKER_RUN) ruff check --fix

# Run tests with pytest
test: wait-services
	@echo "Running tests..."
	$(DOCKER_RUN) pytest -svv

# Install Python dependencies
deps:
	@echo "Installing Python dependencies..."
	$(DOCKER_RUN) pip install --no-cache-dir -r requirements.txt

# Stop all services
stop:
	@echo "Stopping all services..."
	docker compose down

# Clean up all containers and volumes
clean:
	@echo "Cleaning up containers and volumes..."
	docker compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
