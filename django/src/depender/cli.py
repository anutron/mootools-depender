## (c) Copyright 2011 Cloudera, Inc. All rights reserved.

#!/usr/bin/env python
#
# JavaScript depender. A command line tool that concatenates JavaScript files.

import logging
import os
import sys
import imp
from optparse import OptionParser
from core import DependerData

LOG = logging.getLogger(__name__)

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

def build(options, dpdr):
  """
    builds a library given required scripts to includes and other arguments
    accepted arguments:

    option.require     - a comma separated list of components to require. e.g. -r Core/Class,Core/Array
    option.requireLibs - a comma separated list of libraries to require. e.g. -R Core,More
    option.exclude     - exactly like the `require` value, except it's a list of components to exclude.
    option.excludeLibs - exactly like the `exclude` value, except it's a list of libraries to exclude.
    option.compression - true to turn on compression. Not implemented yet.
  """

  def get_arr(val):
    if val:
      return val.split(",")
    else:
      return []

  require = get_arr(options.require)
  exclude = get_arr(options.exclude)
  excludeLibs = get_arr(options.excludeLibs)
  requireLibs = get_arr(options.requireLibs)
  compression = options.compression

  if dpdr is None:
    print >> sys.stderr, "Javascript dependency loader unavailable"

  if compression is None:
    compression = "none"
    # TODO: implement compression
    # compression = dpdr.default_compression

  required = massage(dpdr, require, requireLibs)
  excluded = massage(dpdr, exclude, excludeLibs)

  deps = dpdr.get_transitive_dependencies(required, excluded)
  files = dpdr.get_files(deps, excluded)
  output = "//No files included for build"

  if len(files) > 0:
    #TODO: add copyrights
    output = u""
    output += "\n//This library: %s" % (" ".join(sys.argv),)
    output += "\n//Contents: "
    output += ", ".join([ i.package.key + ":" + i.shortname for i in files ])
    output += "\n\n"

    for f in files:
      output += "// Begin: " + f.shortname + "\n"
      output += f.content + u"\n\n"

  print output

def main():
  usage = "usage: %prog settings.py [options]"

  parser = OptionParser(usage)
  parser.add_option("-r", "--require",     dest="require",     help="a comma separated list of components to require. e.g. -r Core/Class,Core/Array")
  parser.add_option("-R", "--requireLibs", dest="requireLibs", help="a comma separated list of libraries to require. e.g. -R Core,More")
  parser.add_option("-e", "--exclude",     dest="exclude",     help="exactly like the `require` value, except it is a list of components to exclude.")
  parser.add_option("-E", "--excludeLibs", dest="excludeLibs", help="exactly like the `exclude` value, except it is a list of libraries to exclude.")
  parser.add_option("-c", "--compression", dest="compression", help="true to turn on compression. Not implemented yet.")

  (options, args) = parser.parse_args()

  error_msg = "The settings file must be a python file that ends with .py or .pyc."

  if len(args) != 1:
    parser.error(error_msg)

  settings_filepath = args[0]

  mod_name,file_ext = os.path.splitext(os.path.split(settings_filepath)[-1])
  if file_ext.lower() == '.py':
    py_mod = imp.load_source(mod_name, settings_filepath)

  elif file_ext.lower() == '.pyc':
    py_mod = imp.load_compiled(mod_name, settings_filepath)

  else:
    parser.error(error_msg)

  dpdr = DependerData(py_mod.DEPENDER_PACKAGE_YMLS)
  build(options, dpdr)

if __name__ == "__main__":
  main()

