from setuptools import setup, find_packages
import os

from setuptools.dist import Distribution
import pkg_resources


add_django_dependency = True
# See issues #50, #57 and #58 for why this is necessary
try:
    pkg_resources.get_distribution('Django')
    add_django_dependency = False
except pkg_resources.DistributionNotFound:
    try:
        import django
        if django.VERSION[0] >= 1 and django.VERSION[1] >= 1 and django.VERSION[2] >= 1:
            add_django_dependency = False
    except ImportError:
        pass

Distribution({
    "setup_requires": add_django_dependency and  ['Django >=1.1.1'] or []
})


base = os.path.join(os.path.dirname(__file__), "src")

setup(
      name = "depender",
      version = "0.3",
      url = 'http://www.mootools.net',
      description = "Depender: JS Dep loader",
      install_requires = ['setuptools', 'django', 'PyYAML', 'simplejson'],
      packages = find_packages(base),
      package_dir={'': base}
)
