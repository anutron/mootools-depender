#!/usr/bin/env python
#
# JavaScript depender.  Loads and concatenates necessary
# JavaScript files.

import logging

from django.http import HttpResponse
from django.conf import settings
from django.core import urlresolvers
from djangomako.shortcuts import render_to_response, render_to_string
from markdown import markdown
import re

from depender.core import DependerData

LOG = logging.getLogger(__name__)
exclude_blocks = []
if hasattr(settings, 'DEPENDER_EXCLUDE_BLOCKS'):
  exclude_blocks = settings.DEPENDER_EXCLUDE_BLOCKS

def make_depender():
  return DependerData(settings.DEPENDER_PACKAGE_YMLS, settings.DEPENDER_SCRIPTS_JSON, exclude_blocks)

depender = make_depender()

def get_depender(reset):
  global depender
  if settings.DEPENDER_DEBUG:
    return make_depender()
  else:
    if reset == "true":
      depender = make_depender()
    return depender

def massage(depender, components, packages):
  """
  @param depender: A DependerData object
  @param components: Component names, in either package/component format, or just
    "naked" (hopefully unique) components.
  @param packages: Package names, which expand into their constituent components.
  @return A set of all components specified.
  """
  ret = set()
  for package in packages:
    ret.update(depender.expand_package(package))
  for component in components:
    if "/" in component:
      ret.add( tuple(component.split("/", 2)) )
    else:
      ret.add( depender.resolve_unqualified_component(component) )
  return ret

def build(request):
  """
    builds a library given required scripts to includes and other arguments
    accepted URL arguments:

    require - a comma separated list of *files*(components) to require; can also be specified as "require=foo&require=bar"
    requireLibs - a comma separated list of *libraries*(packages) to require - these are the names defined in our *congfig.json* in the *libs* section. So, for example, *requireLibs=mootools-core,mootools-more* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list oras (*requireLibs=mootools-core&requireLibs=mootools-more*).
    exclude - exactly like the *require* value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
    excludeLibs - just like the *exclude* option but instead you can specify entire libraries.
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

  try:
    dpdr = get_depender(reset)
  except Exception, inst:
    return HttpResponse("alert('Javascript dependency loader unavailable. Contact your administrator to check server logs for details.\n [" + str(inst).replace("'", "\\'") +  "]')")
    
  if compression is None:
    compression = "none"
    # TODO: implement compression
    # compression = dpdr.default_compression
  if settings.DEPENDER_DEBUG:
    compression = "none"

  if client == "true" and "Depender.Client" not in require:
    require.append("Depender.Client")

  required = massage(depender, require, requireLibs)
  excluded = massage(depender, exclude, excludeLibs)

  deps = dpdr.get_transitive_dependencies(required, excluded)
  files = dpdr.get_files(deps, excluded)
  output = "//No files included for build"

  if len(files) > 0:
    #TODO: add copyrights
    #TODO: add link to download link
    #TODO: add download file stuff
    output = u""
    output += "\n//This library: " + request.build_absolute_uri(request.get_full_path())
    output += "\n//Contents: "
    output += ", ".join([ i.package.key + ":" + i.shortname for i in files ])

    if len(exclude_blocks) > 0:
      output += "\n//Excluded blocks: "
      output += ", ".join(exclude_blocks)

    output += "\n\n"

    for f in files:
      output += "// Begin: " + f.shortname + "\n"
      output += f.content + u"\n\n"

  if client == "true":
    try:
      url = request.build_absolute_uri(
        urlresolvers.reverse("depender.views.build"))
    except Exception:
      url = "/depender/build"
    output += dpdr.get_client_js(deps, url)

  response = HttpResponse(output, content_type="application/x-javascript")
  if download == "true":
    response['Content-Disposition'] = 'attachment; filename=built.js'
  return response
build.login_notrequired = True

def builder(request):
  dpdr = get_depender(False)
  packages = {}
  #Core, More, etc
  for p in settings.BUILDER_PACKAGES:
    if not hasattr(packages, p):
      packages[p] = {}
    #Fx, Element, etc
    for name, component in dpdr.packages[p].components.iteritems():
      if not hasattr(packages[p], component.filename):
        packages[p][component.filename] = {
          'provides': [],
          'requires': []
        }
      packages[p][component.filename]['provides'].extend(component.provides)
      packages[p][component.filename]['requires'].extend(component.requires)
  def get_provides(package, filename):
    return [pc[1] for pc in packages[package][filename]['provides']]
  def get_depends(package, filename):
    return [pc[0] + '/' + pc[1] for pc in packages[package][filename]['requires']]
  return render_to_response('packager.mako', 
    {
      'packages': settings.BUILDER_PACKAGES,
      'package_data': packages,
      'get_provides': get_provides,
      'get_depends': get_depends,
      'dpdr': dpdr,
      'markdown': markdown
    }
  )

def test(request):
  #this seems silly
  import os
  p = os.path.join(os.path.dirname(__file__), "static", "test.html")
  f = file(p)
  return HttpResponse(f.read())
