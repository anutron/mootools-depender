# Minimal Django settings for mootools depender.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'mootools.urls'

INSTALLED_APPS = (
    'mootools.depender'
)

# Depender configuration
import os
import logging

logging.basicConfig(level=logging.INFO)
DEPENDER_ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")
DEPENDER_CONFIG_JSON = os.path.join(os.path.dirname(__file__), "../../config/config.json")
DEPENDER_YUI_PATH = os.path.join(os.path.dirname(__file__), "../../compressors/yuicompressor-2.4.2.jar")
DEPENDER_DEBUG = False
