#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import structlog

# Configure structlog for logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger(__name__)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        logger.critical(
            "Couldn't import Django. Ensure it's installed and available on your "
            "PYTHONPATH environment variable. Did you forget to activate a virtual environment?",
            exc_info=True,
        )
        sys.exit(1)

    try:
        execute_from_command_line(sys.argv)
    except Exception:
        logger.exception("An error occurred while executing the command.")
        sys.exit(1)


if __name__ == '__main__':
    main()
