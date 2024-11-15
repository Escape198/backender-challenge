#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

logger = logging.getLogger(__name__)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    if not os.getenv('DJANGO_SETTINGS_MODULE'):
        logger.error("The environment variable 'DJANGO_SETTINGS_MODULE' is not set.")
        sys.exit(1)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.critical(
            "Couldn't import Django. Ensure it's installed and available on your "
            "PYTHONPATH environment variable. Did you forget to activate a virtual environment?",
            exc_info=True,
        )
        sys.exit(1)

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        logger.exception("An error occurred while executing the command.")
        sys.exit(1)


if __name__ == '__main__':
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    main()
