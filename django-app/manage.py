#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'synker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    
    main()

    # if not os.environ.get('SYNKER_RUNNING', None):
    # @TODO: Make this modular
    from multiprocessing import Process
    from sync_utils.runner import run

    print("Starting synker process")
    synker_process = Process(target=run)
    synker_process.start()

