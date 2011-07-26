#!/usr/bin/env python

from django.core.management.base import NoArgsCommand
from depender import views
from django.conf import settings

class Command(NoArgsCommand):
  """
  Runs depender's self_check command.  Effectively
  initializes depender.
  """
  def handle_noargs(self, **options):
    for version, config in settings.PROJECTS.iteritems():
      depender = views.get_depender(version)
      depender.self_check()
