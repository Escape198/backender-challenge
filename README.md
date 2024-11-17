# Die Hard

This project is a test assignment for backend developers. It implements the basic functionality of a web application using Python and Django, while also supporting an extensible architecture for event handling and logging.

## Technologies

The project is built using the following technologies:

- Python 3.13
- Django 5
- Celery
- Redis
- PostgreSQL
- ClickHouse
- pytest
- structlog
- Docker and Docker Compose

## Setup and Running

### Environment Preparation

1. Ensure Docker and Docker Compose are installed.
2. Create a `.env` file in the `src/core` directory. You can start with an example:

```bash
cp src/core/.env.ci src/core/.env
```
### Environment Variable Configuration

In the `.env` file, set the following variables:

- `DEBUG` - Set to `True` for development mode, or `False` for production.
- `SECRET_KEY` - Django secret key.
- `DATABASE_URL` - PostgreSQL connection string.
- `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` - Parameters for connecting to ClickHouse.
- `REDIS_URL` - URL for connecting to Redis.
- `SENTRY_CONFIG_DSN` - DSN for integrating with Sentry.
- `SENTRY_CONFIG_ENVIRONMENT` - Sentry environment name.

### Running the Containers

To start the project, run the following:

```bash
make run
```
After that, install the required dependencies and run migrations:
```bash
make install
```
## Testing

To run the tests, use the following command:
```bash
make test
```
The tests include integration with ClickHouse, validation of the transactional outbox model, and unit tests.

## Code Quality Check

The project uses `ruff` for code quality analysis. To run the linter:
```bash
make lint
```
You can automatically fix most code issues.

## Project Features

### User Management

- User registration using the `User` model.
- Logging user actions via the `EventLogClient`.

### Transactional Outbox Model

The `transactional_outbox` mechanism guarantees atomicity in event processing and their recording in ClickHouse.

### Sentry Integration

Errors are automatically sent to Sentry for monitoring if the `SENTRY_CONFIG_DSN` variable is set.

### Asynchronous Task Processing

Celery is used for asynchronous task handling. Event logging tasks are reliably executed, thanks to the transactional model.

## Running Options

- Development mode with `DEBUG=true`.
- Production mode with enhanced security (CSRF_COOKIE_SECURE and SECURE_HSTS_SECONDS settings).
- Option to run with Django's built-in server (runserver) or Gunicorn for production.
- Ability to override environment variables without modifying the source code.

## Project Structure

- `src/core` - Core Django settings, including middleware and database configuration.
- `src/users` - Application for managing users.
- `src/tests` - Tests covering application logic and integration with external services.
- `docker` - Directory with Docker Compose configuration, including settings for PostgreSQL and ClickHouse.

## Feedback

If you have any suggestions or comments on the project, please create an issue or pull request in the repository. We welcome any feedback!

## Author
