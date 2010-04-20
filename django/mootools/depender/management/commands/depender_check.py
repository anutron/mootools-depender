#!/usr/bin/env python
# (c) Copyright 2010 Cloudera, Inc. All rights reserved.

from django.core.management.base import NoArgsCommand
from depender import views

class Command(NoArgsCommand):
  """
  Runs depender's self_check command.  Effectively
  initializes depender.
  """
  def handle_noargs(self, **options):
    views.depender.self_check()
