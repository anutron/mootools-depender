#!/usr/bin/env python
#
# JavaScript depender.  Loads and concatenates necessary
# JavaScript files.

import logging

from django.http import HttpResponse
from django.conf import settings
from django.core import urlresolvers
import re

from depender.core import DependerData

LOG = logging.getLogger(__name__)

def make_depender():
  return DependerData(settings.DEPENDER_PACKAGE_YMLS, settings.DEPENDER_SCRIPTS_JSON)

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
    blocks - specify which code blocks to *include*. You can specify them as blocks=1.2compat,1.3compat, as blocks=1.2compat&block=1.3compat or blocks=all (to include all code blocks)
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
  blocks = get_arr("blocks")
  exclude_blocks = get_arr("excludeBlocks")

  if len(blocks) == 0:
    blocks = settings.DEPENDER_INCLUDE_BLOCKS
  if len(exclude_blocks) == 0:
    exclude_blocks = settings.DEPENDER_EXCLUDE_BLOCKS
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
  js = ""

  if len(files) > 0:
    #TODO: add copyrights
    #TODO: add link to download link
    #TODO: add download file stuff
    output = u""
    output += "\n//This library: " + request.build_absolute_uri(request.get_full_path())
    output += "\n//Contents: "
    output += ", ".join([ i.package.key + ":" + i.shortname for i in files ])

    for f in files:
      js += "// Begin: " + f.shortname + "\n"
      js += f.content + u"\n\n"

  if client == "true":
    url = request.build_absolute_uri(
      urlresolvers.reverse("depender.views.build"))
    js += dpdr.get_client_js(deps, url)

  included_blocks = []
  def block_matcher(matchobj):
    """
    Finds code blocks that should be included/excluded based on url params.
    JS code can be marked with named blocks, for example:
    
      //<1.2compat>
      ...compat code
      //</1.2compat>
    
    The request to Depender can include ?blocks=all or ?blocks=1.2compat,1.3compat,etc
    and the block will be removed or included accordingly.
    You can also state ?excludeBlocks=... to include all blocks but a specific list
    """
    match = matchobj.group(0)
    block = re.search('<(.*?)>', match).group(1)
    if (block in blocks or 'all' in blocks or len(blocks) == 0) and\
      not (block in exclude_blocks or 'all' in exclude_blocks):
      if block not in included_blocks:
        included_blocks.append(block)
      return match
    else:
      return ''
  js = re.sub(r'((/[/*])\s*<([^>]*)>.+?<\/\3>(?:\s*\*/)?(?s))', block_matcher, js)
  if len(included_blocks) > 0:
    output += "\n//included blocks: " + ", ".join(included_blocks)
  output += "\n\n"
  output += js

  response = HttpResponse(output, content_type="application/x-javascript")
  if download == "true":
    response['Content-Disposition'] = 'attachment; filename=built.js'
  return response
build.login_notrequired = True

def test(request):
  #this seems silly
  import os
  p = os.path.join(os.path.dirname(__file__), "static", "test.html")
  f = file(p)
  return HttpResponse(f.read())
