#!/usr/bin/env python2.5

from django.conf.urls.defaults import *

urlpatterns = patterns('depender',
  url(r'^build$', 'views.build'),
  url(r'^test$', 'views.test')
)
