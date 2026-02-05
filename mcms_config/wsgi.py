"""
WSGI config for MCMS project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcms_config.settings')

application = get_wsgi_application()
