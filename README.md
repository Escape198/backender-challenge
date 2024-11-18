# Die Hard

This project is a test assignment for backend developers. It implements the basic functionality of a web application using Python and Django, while also supporting an extensible architecture for event handling and logging.

---

## Technologies

The project is built using the following technologies:

- **Python** 3.13
- **Django** 5
- **Celery** for asynchronous task management
- **Redis** as a message broker and caching system
- **PostgreSQL** as the primary database
- **ClickHouse** for event logging and analytics
- **pytest** for testing
- **structlog** for structured and context-aware logging
- **Docker** and **Docker Compose** for containerized development and deployment

---

## Setup and Running

### **Environment Preparation**

1. Ensure Docker and Docker Compose are installed.
2. Create a `.env` file in the `src/core` directory. You can use the provided example configuration:
   ```bash
   cp src/core/.env.ci src/core/.env
   ```
   
### **Environment Variable Configuration**

In the `.env` file, configure the following variables:

- `DEBUG` - Set to `True` for development mode, or `False` for production.
- `SECRET_KEY` - Django secret key.
- `DATABASE_URL` - PostgreSQL connection string (e.g., `postgres://user:password@host:port/dbname`).
- `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` - Parameters for connecting to ClickHouse.
- `REDIS_URL` - URL for connecting to Redis (e.g., `redis://user:password@host:port/0`).
- `SENTRY_CONFIG_DSN` - DSN for Sentry integration (optional).
- `SENTRY_CONFIG_ENVIRONMENT` - Environment identifier for Sentry.

---

### **Running the Application**

1. **Start the Docker containers**:
   ```bash
   make run
   ```
2. **Install dependencies and prepare the database**:
   ```bash
   make install
   ```

This includes:
   - Applying database migrations
   - Creating a superuser (if required)

3. **Access the application**:
   - Development mode: `http://localhost:8000`
   - APIs and other endpoints are available under the `/api/` namespace.

---

## Testing and Quality Assurance

### **Run Tests**
Execute the test suite using:
```bash
make test
```

- Includes unit tests, integration tests with ClickHouse, and validation of the transactional outbox model.

### **Code Quality Check**
Run the linter (using `ruff`) to ensure code quality:
```bash
make lint
```

- Automatically fixes most code style issues.

---

## Key Features

### **User Management**
- Supports user registration and authentication using the `User` model.
- Logs user actions with the `EventLogClient`, ensuring detailed and structured event tracking.

### **Transactional Outbox Model**
- Implements a **transactional outbox pattern** to ensure atomicity in event processing.
- Guarantees safe delivery of events to ClickHouse.

### **Asynchronous Task Processing**
- Uses Celery to handle background tasks like event logging reliably.
- Tasks are configured with retry mechanisms to handle transient failures.

### **Structured Logging**
- Leverages `structlog` for enriched, context-aware logging.
- Provides detailed logs for task execution, errors, and database operations.

### **Sentry Integration**
- Automatically sends error reports to Sentry if `SENTRY_CONFIG_DSN` is set.
- Enables proactive monitoring and debugging.

### **Development and Production Modes**
- Development mode:
  - `DEBUG=True`
  - Fast development server (Django runserver)
- Production mode:
  - Security enhancements like `CSRF_COOKIE_SECURE` and `SECURE_HSTS_SECONDS`
  - Configurable with Gunicorn or other WSGI servers.

---

## Project Structure

- `src/core/` - Core configuration for Django (settings, middleware, database).
- `src/users/` - User-related functionality (models, serializers, use cases).
- `src/tests/` - Comprehensive test suite for unit and integration testing.
- `docker/` - Docker Compose configurations and initialization scripts for services.

---

## Known Limitations and Planned Improvements

- **Event Duplication**: Current implementation of the outbox pattern may lead to duplicate events if a worker crashes mid-task. Improvements to handle this scenario are planned.
- **Tracing**: While `structlog` provides detailed logs, integration with tools like OpenTelemetry for full tracing support is under consideration.
- **Enhanced Testing**: Increasing test coverage, especially for ClickHouse integrations, and reducing reliance on mocks.
- **Environment Configuration**: Some variables (e.g., `REDIS_URL`) are hardcoded and should be dynamically loaded from `.env`.

---

## Feedback and Contribution

We welcome feedback and contributions! If you have suggestions, issues, or would like to contribute to this project:
1. Create an issue on GitHub.
2. Submit a pull request with your changes.

---

## Author

This project is developed as part of a backend developer assignment. For inquiries, contact us via the repository issue tracker.