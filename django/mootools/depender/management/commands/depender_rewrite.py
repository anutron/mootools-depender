#!/usr/bin/env python
# (c) Copyright 2010 Cloudera, Inc. All rights reserved.

from django.core.management.base import NoArgsCommand
from depender import views

class Command(NoArgsCommand):
  """
  Rewrites all script_json packages to use package.yml
  syntax.
  """
  def handle_noargs(self, **options):
    for p in views.depender.script_json_packages:
      p.rewrite()
