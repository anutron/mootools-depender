#!/usr/bin/env python2.5
#
# JavaScript depender.  Loads and concatenates necessary
# JavaScript files.

import logging
import datetime
from email.Utils import mktime_tz, parsedate_tz
import re
import time

from django.http import HttpResponse, HttpResponseNotModified
from django.utils.http import http_date
from django.conf import settings

from depender.core import Depender

LOG = logging.getLogger(__name__)

def make_depender():
  depender = Depender(settings.DEPENDER_ROOT, settings.DEPENDER_CONFIG_JSON, settings.DEPENDER_DEBUG)
  return depender

depender = make_depender()
server_started = time.time()

def build(request):
  """
    builds a library given required scripts to includes and other arguments
    accepted URL arguments:

    require - a comma separated list of *files* to require; can also be specified in the php style as "require[]=foo&require[]=bar"
    requireLibs - a comma separated list of *libraries* to require - these are the names defined in our *congfig.json* in the *libs* section. So, for example, *requireLibs=mootools-core,mootools-more* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list or the php style (*requireLibs[]=mootools-core&requireLibs[]=mootools-more*).
    exclude - exactly like the *require* value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
    excludeLibs - just like the *exclude* option but instead you can specify entire libraries.
    cache - if set to *true* you'll be returned a cached version of the script even if the server is set to *false* and vice versa.
    compression - you'll be returned the compression type you specify regardless of the server default. Note that if you specify a compression type that the server does not allow, you'll be returned which ever one it does. If it does not support compression at all, you will not be returned a compressed file. You can also specify "none" which is useful for development and debugging.
    
  """
  
  def get(name):
    return request.GET.get(name)
  def get_arr(name):
    val = get(name)
    if val:
      return val.split(",")
    else:
      return []

  require = get_arr("require")
  exclude = get_arr("exclude")
  excludeLibs = get_arr("excludeLibs")
  requireLibs = get_arr("requireLibs")
  download = get("download")
  reset = get("reset")
  client = get("client")
  compression = get("compression")

  dpdr = None
  global depender
  if settings.DEPENDER_DEBUG:
    dpdr = make_depender()
  else:
    dpdr = depender
  if reset == "true":
    depender = dpdr
    
  if compression is None:
    compression = dpdr.default_compression
  if settings.DEPENDER_DEBUG:
    compression = "none"

  last_modified_header = request.META.get('HTTP_IF_MODIFIED_SINCE')
  LOG.info("last mondified header: " + str(last_modified_header))
  if (last_modified_header and extract_last_modified_time(last_modified_header) >= server_started
      and not settings.DEPENDER_DEBUG and not reset == "true"):
    return HttpResponseNotModified()

  if client == "true" and require.count("Depender.Client") == 0:
    require.append("Depender.Client")
  
  includes = dpdr.get_dependencies(require, exclude, requireLibs, excludeLibs)
  output = "//No files included for build"
  if len(includes) > 0:
    
    libraries_and_copyrights = dict()
    for i in includes:
      libraries_and_copyrights[i.library] = i.copyright

    output = ""
    for lib, copy in libraries_and_copyrights.iteritems():
      if len(copy) > 0:
        output += copy + "\n"

    output += "\n//Contents: "
    output += ", ".join([ i.name for i in includes ])
    output += "\n\n"
  
    location = request.META["SERVER_PROTOCOL"].split("/")[0].lower() + "://" + request.META["HTTP_HOST"] + request.path
    args = request.META["QUERY_STRING"]
    if args.find("download=") >= 0:
      clean = []
      for arg in args.split("&"):
        if arg.find("download=") == -1:
          clean.append(arg)
      args = '&'.join(clean)

    output += "//This lib: " + location + '?' + args
    output += "\n\n"
  
  
    for i in includes:
      output += i.compressed_content[compression] + "\n\n"

    if client == "true":
      output += dpdr.get_client_js(includes, location)

  response = HttpResponse(output, content_type="application/x-javascript")
  response["Last-Modified"] = http_date(server_started)
  
  if (download == "true"):
    response['Content-Disposition'] = 'attachment; filename=built.js'
  return response

build.login_notrequired = True

def extract_last_modified_time(header):
  """
  Extracts time from the HTTP_IF_MODIFIED_SINCE header.
  Based on django's django.static.views:was_modified_since
  """
  LOG.info('header: ', header)
  matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header, re.IGNORECASE)
  header_mtime = mktime_tz(parsedate_tz(matches.group(1)))
  header_len = matches.group(3)


def test(request):
  #this seems silly
  return HttpResponse(file(settings.DEPENDER_ROOT + '/mootools/depender/static/test.html').read())
