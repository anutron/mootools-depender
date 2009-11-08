#!/usr/bin/env python2.5

import os

from django.conf import settings
from django.utils.datastructures import SortedDict

import logging
import subprocess
import simplejson

LOG = logging.getLogger(__name__)

class Depender(object):
  """
  The base class for this application; loads all the scripts, compresses them, 
  and retains them in memory awaiting requests to concatenate scripts for repsonse.
  """
  def __init__(self, root, config_file, debug=False):
    """
    @param root: Root directory relative to which to resolve scripts.json
    references.
    @param config_file: Configuration file for Depender, which
    contains links to other config.json's.
    """
    self.script_root = root
    self.debug = debug
    self.conf = self.parse_configuration(config_file)
    self.default_compression = self.conf['compression']
    self.initialize_compressors()
    self.load_everything()
    
  def initialize_compressors(self):
    """
    creates instances of supported compressors (defaults only to YUI)
    """
    self.supported_compressors = {
      "yui": YUI()
    }
    self.compressors = {}
    for compression in self.conf['available_compressions']:
      if (self.supported_compressors.get(compression)): self.compressors[compression] = self.supported_compressors[compression]
    
  def relative(self, path):
    """
    converts a path to the full path relative to the depender root
    """
    return os.path.join(self.script_root, path)

  def parse_json_relative(self, path):
    "Returns decoded representation of JSON file at path."
    f = file(self.relative(path))
    o = simplejson.load(f)
    return o

  def parse_configuration(self, config):
    """
    parses a configuration file (config.json) to be the configuration for the Depender instance"
    """
    conf = self.parse_json_relative(config)
    return conf

  def get_scripts(self, library):
    """
    Gets all the scripts for a library and instantiates them as a Script, 
    returning them in an array.
    """
    base = self.conf["libs"][library]["scripts"]
    scripts = self.parse_json_relative(os.path.join(base, "scripts.json"))
    ret = []
    for cat, cat_data in scripts.iteritems():
      for script, data in cat_data.iteritems():
        path = self.relative(os.path.join(base, cat, script + ".js"))
        s = Script(library=library, category=cat, name=script, 
          path=path, data=data, compressors=self.compressors, debug=self.debug,
          copyright=self.conf["libs"][library].get('copyright', ''))
        ret.append(s)
    return ret

  def load_everything(self):
    """
    Loads all scripts defined in config.json's 'libs' section into memory
    """
    self.all_scripts = SortedDict()
    self.conf["libs"]["depender-client"] = {
      "scripts": self.script_root + "/../client/Source"
    }
    for library in self.conf["libs"]:
      scripts = self.get_scripts(library)
      for s in scripts:
        if s.name in self.all_scripts:
          raise Exception("%s defined in two libraries: %s and %s" % 
            (s.name, self.all_scripts[s.name].library, s.library))
        self.all_scripts[s.name] = s
    # Map the raw_deps (which are strings) into the objects
    for script in self.all_scripts.itervalues():
      try:
        script.deps = [ self.all_scripts[x] for x in script.raw_deps ]
      except KeyError:
        raise Exception("%s could not be found in any library" % x)

  def accumulate_dependencies(self, script, accumulated_list, accumulated_set):
    """
    determines the dependencies for a script
    """
    for dep in script.deps:
      if dep is not script and dep not in accumulated_set:
        self.accumulate_dependencies(dep, accumulated_list, accumulated_set)
    if script not in accumulated_set:
      accumulated_list.append(script)
      accumulated_set.add(script)
  
  def get_dependencies(self, include_names, exclude_names, include_lib_names, exclude_lib_names):
    """
    Recursively gather all dependencies for script, ignoring
    dependencies in exclude.
    """
    for lib in include_lib_names:
      for script in self.get_scripts(lib):
        include_names.append(script.name)
    for lib in exclude_lib_names:
      for script in self.get_scripts(lib):
        exclude_names.append(script.name)

    scripts = [ self.all_scripts[name] for name in include_names ]
    excludes = [ self.all_scripts[name] for name in exclude_names ]
    
    acc_list = []
    acc_set = set(excludes)
    for s in scripts:
      self.accumulate_dependencies(s, acc_list, acc_set)
      
    assert len(acc_list) == len(set(acc_list))
    return acc_list

  def get_client_js(self, scripts, url):
    """
    returns the javascript necessary to integrate with Depender.Client.js
    """
    out = "\n\n"
    out += "Depender.loaded.combine(['"
    out += "','".join([ i.name for i in scripts ]) + "']);\n\n"
    out += "Depender.setOptions({\n"
    out += "	builder: '" + url + "'\n"
    out += "});"
    return out;
  
  def get_output_filename(self):
    """
    returns the filename for the header if download=true
    """
    return self.conf.get('output filename', 'built.js')

class Script(object):
  def __init__(self, library, category, name, path, data, compressors, copyright, debug=False):
    """
    Instantiates a script object.
    library - the library, as defined in config.json, to which the script belongs
    category - the category, as defined in scripts.json, to which the script belongs
    name - the name of the script (without the .js - so "Core", not "Core.js")
    path - the path to the file relative to this application
    data - the data associated with the script as defined in scripts.json; in particular, the dependencies
    compressors - a list of compressors to apply to the script (["yui"] for example)
    """
    self.raw_deps = data["deps"]
    self.description = data.get("desc")
    self.category = category
    self.path = path
    self.library = library
    self.name = name
    self.copyright = copyright
    self.debug = debug
    content = file(self.path).read()

    self.compressed_content = {}
    if not self.debug:
      for compressor_name, compressor in compressors.iteritems():
        LOG.info("compressing %s.js with %s" %(name, compressor_name))
        self.compressed_content[compressor_name] = compressor.compress(name, content)
    self.compressed_content["none"] = content
    
  def __repr__(self):
    return "Script(%s)" % self.name

class YUI(object):
  def __init__(self, arguments=None):
    """
    creates an instance of the YUI compressor with default arguments or those specified.
    arguments default to: "--type js --preserve-semi --line-break 150 --charset UTF-8"
    """
    if arguments is None:
      arguments = [
        "--type", "js",
        "--preserve-semi",
        "--line-break", "150",
        "--charset", "UTF-8"
      ]
    self.arguments = arguments
    self.executable = settings.DEPENDER_YUI_PATH

  def compress(self, name, content):
    """
    compresses a script using the yui compressor
    name - the name of the script (used for error reporting)
    content - the content of the script
    """
    args = ["java", "-jar", self.executable]
    args.extend(self.arguments)
    pipe = subprocess.Popen(args=args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = pipe.communicate(input=content)
    if pipe.returncode != 0:
      import pdb
      pdb.set_trace()
      logging.debug(content);
      raise Exception("YUI compressor failed on %s, out: %s, error: %s" % (name, out, error) )
    return out

