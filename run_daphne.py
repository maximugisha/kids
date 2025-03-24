# run_daphne.py
import os
import sys

import django
from django.core.asgi import get_asgi_application

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_diy.settings")

# Initialize Django
django.setup()

if __name__ == "__main__":
    # Import and run Daphne programmatically
    from daphne.cli import CommandLineInterface

    sys.argv = ["daphne", "-b", "127.0.0.1", "-p", "8001", "kids_diy.asgi:application"]
    CommandLineInterface().run()
