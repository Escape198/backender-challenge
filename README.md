# Die Hard

This is a project with a test task for backend developers.

## Detailed Requirements

You can find the detailed requirements by clicking the links:
- [English version](docs/task_en.md)
- [Russian version](docs/task_ru.md)

## Tech Stack

The project uses the following technologies:
- **Python 3.13**: The latest Python version for backend development.
- **Django 5**: A modern web framework.
- **pytest**: For robust and flexible testing.
- **Docker & docker-compose**: For containerization and orchestration.
- **PostgreSQL**: As the primary relational database.
- **ClickHouse**: For analytics and log storage.

## Installation

### Step 1: Environment Variables

Place a `.env` file into the `src/core` directory. You can start with a template file by running:

```bash
cp src/core/.env.ci src/core/.env
```

In this file, ensure you configure the following variables:
- **`DEBUG`**: Set to `true` or `false`.
- **`DATABASE_URL`**: Connection string for the PostgreSQL database.
- **`CLICKHOUSE_URL`**: Connection string for the ClickHouse instance.
- **`SECRET_KEY`**: Your Django secret key.

### Step 2: Run Containers

Start the application containers with:

```bash
make run
```


This will set up the environment with Docker.

### Step 3: Install Dependencies and Migrate

After starting the containers, run the installation script:

```bash
make install
```

This will:
- Apply database migrations.
- Create a superuser account.

---

## Testing

Run the test suite using:

```bash
make test
```

This command executes all tests with `pytest`.
- Results will display detailed information about passed, failed, and skipped tests.

---

## Linter

Run the linter to ensure code quality:

```bash
make lint
```

This command runs `ruff` for linting.

- If fixable issues are found, they will be automatically corrected.
- Non-fixable issues will need manual intervention.
- Linting checks ensure your code follows the defined style guidelines and best practices.

---

## Available Makefile Commands

Below is a summary of available commands from the `Makefile`:

- **`make run`**: Starts the application containers.
- **`make install`**: Runs migrations and sets up the application.
- **`make migrations`**: Creates new Django migrations.
- **`make migrate`**: Applies existing migrations to the database.
- **`make superuser`**: Creates a new superuser for the Django application.
- **`make shell`**: Opens an interactive Django shell inside the container.
- **`make test`**: Runs the test suite using `pytest`, providing detailed output for each test.
- **`make lint`**: Lints the code using `ruff` and fixes any fixable issues.

---

## Feedback

If you encounter any issues or have suggestions for improvement, feel free to create an issue in the repository. Contributions are welcome!

---