#!/usr/bin/env python2.5

from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^build$', 'depender.views.build'),
  url(r'^test$', 'depender.views.test'),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root': '../../styles'}),
)
