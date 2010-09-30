Depender: A MooTools Dependency Loader
======================================

This application generates concatenated libraries from multiple JavaScript files based on their dependencies and the files you require.

Quick Start (Django version)
-----------

		$ git clone http://github.com/anutron/mootools-depender.git
		$ cd mootools-depender
		$ git submodule update --init
		$ virtualenv env
		$ env/bin/python django/setup.py develop
		$ env/bin/python django/mootools/manage.py runserver
		
		Then open http://localhost:8000/depender/build?requireLibs=Core to get MooTools Core.

requirements:

* [virtualenv](http://pypi.python.org/pypi/virtualenv)
* [python](http://www.python.org/)

To install virtualenv on OSX, follow these instructions ([more on virtualenv](http://www.fprimex.com/coding/pymac.html)):

	# Install easy_install and virtualenv into the system wide python package dir
	curl -O http://peak.telecommunity.com/dist/ez_setup.py > ez_setup.py
	sudo python ez_setup.py
	sudo easy_install virtualenv
	rm ez_setup.py

Highlights
----------

Depender can:

* check and enforce decencies on startup
* it can also expressly just check dependencies on the command line and exit
* return a library to you with only the things you require
* return a library with what you require LESS things you already have (i.e. require=foo&exclude=bar)
* is a standalone Django app, making it deployable; it does not rely on apache / php or any other server environment
* can include in its response a JS library for loading more JS dependencies on the fly
* includes in its response a list of what is in the response and a url to recreate it
* can convert scripts.json to yaml headers and write them to JS files for you
* can convert yaml headers to scripts.json and write that to a file
* can work with both yaml header projects and scripts.json projects at the same time
* reads the entire library state into RAM, making it very, very fast; it is production ready
* can be run in debug mode, always reading from disk to allow for live development
* can be integrated with memcache for faster results
* can be configured to return compressed files; this compression only runs on startup
* can return libraries based on individual requirements (require=Core/Request) OR entire libraries (requireLib=Core)
* as a django app, it can be deployed inside another django app, meaning that you only need to start one server for your application

Overview
-------

While this application can be used without MooTools to build libraries from other sources, it makes use of certain conventions tied to the MooTools JavaScript library and the manner in which its files are organized. In particular, the use of yaml headers to declare dependencies.

The purpose of this application is to allow users to build their own libraries using MooTools files and files of their own. It can, if you choose, be used in a live environment to deliver scripts on the fly. It's often more appropriate, especially for high-traffic applications, to use this application to output libraries and save these for deployment as static files. Linking to the application directly may produce a demand on server resources that is not acceptable. That said, this application reads the libraries to RAM and is very fast. Further, it can be configured to use something like [memcached](http://memcached.org/) for improved performance.

This application is a [Django](http://www.djangoproject.com/) application. Additionally, there is a client library - Depender.Client.js - that allows for interactive, lazy-loading of required libraries. Using this client requires that you pull scripts from the Depender server, which depending on the load of your application, may not be acceptable.

Django Configuration
-------------------

Depender supports both the "old" scripts.json method for naming package contents and dependencies (which suffers from a requirement that ALL scripts be named uniquely) but also the newer method that MooTools supports using YAML based manifests and headers. The package.yml and YAML fragments define package names and component names and [can be found described on the MooTools Forge in detail](http://mootools.net/forge/how-to-add). Note that the tag is not used in dependency requirements and the asterisk value is not supported. You cannot do this:

	requires: [Core/1.2.4:'*']

If you specify a tag (the `1.2.4:` above) it will be ignored. Here is a valid YAML header sample:

	/*
	---

	script: Fx.Accordion.js

	description: An Fx.Elements extension which allows you to easily create accordion type controls.

	license: MIT-style license

	authors:
	- Valerio Proietti

	requires:
	- Core/Element.Event
	- Fx.Elements
	
	## requires: [Core/Element.Event, Fx.Elements] << also valid

	provides: Fx.Accordion

	## provides: [Fx.Accordion] << also valid
	...
	*/

Depender is a standard Django application that can be included in any project (see the Django docs to learn [the differences between applications and projects](http://docs.djangoproject.com/en/dev/intro/tutorial01/#creating-a-project)). It ships with a simple project called "mootools" that includes the Depender application and is configured to build MooTools Core and MooTools More.

Configuring the MooTools Depender Project
========================================

Inside of `django/mootools` you'll find `settings.py`. This file contains all the configuration options for the simple "mootools" project which includes the Depender app. You'll find the following options that you may set:

 - DEPENDER_DEBUG - set to `True` (the default) if you want Depender to always load scripts from the disk (i.e. disable memory caching). This also disabled compression. Note that this is somewhat slow-ish, as every request requires the app to load ALL the JS into memory. **Note** you can set this as an environment variable if you prefer.
 - DEPENDER_PACKAGE_YMLS - a list of package.yml files to include; defaults to the submodules included in this repository (MooTools Core and MooTools More) as well as the Depender Client.
 - DEPENDER_SCRIPTS_JSON - a list of scripts.json manifest files (these are deprecated manifests from < Mootools 1.3 era).
 - DEPENDER_YUI_PATH - the path to the YUI compressor jar.

Initialization
--------------
The application ships with two git submodule settings - one for the most recent, stable release of MooTools Core and another for MooTools More. Though the application does not require these to function, most people will wish to include these. To initialize these libraries you must execute at the command line:

	git submodule update --init

This will download the libraries. 

To run the Django depender server you should simply run this from the command line in the root of the repository:

	$ virtualenv env 
	$ env/bin/python django/depender/setup.py develop
	$ env/bin/python django/mootools/manage.py runserver

If you want you can force the server to run in debug mode like so:

	$ DEPENDER_DEBUG=1 env/bin/python django/mootools/manage.py runserver

You can have Depender check your dependency map thusly:

	$ env/bin/python django/mootools/manage.py depender_check

For more about virtualenv see [http://pypi.python.org/pypi/virtualenv](http://pypi.python.org/pypi/virtualenv). Once you've started the server you should be able to hit it with a request for some JS. Like this:

	http://localhost:8000/depender/build?requireLibs=Core

Adding Libraries
----------------
Additional libraries can be easily added to the system by dropping their contents into the libs/ directory and editing the appropriate config file (they do not have to reside in the libs/ directory; so long as the config points to the appropriate location). You can use git submodules to track specific branches of external repositories or you can track a working branch using something like [crepo](http://github.com/cloudera/crepo/tree/master). 

Compression
-----------

Depender makes use of the [YUI compressor](http://developer.yahoo.com/yui/compressor/). It doesn't cache results to disk but rather to memory, which makes it much faster and more ideal for actual deployment. Startup is slow, as it compresses everything, but after this the application is very fast. Note that if you change files on the disk, the application will not pick up these changes until you restart it (unless you are in debug mode; see the section on Django Settings above). Compression is disabled in debug mode.

Headers and Output
-------
Each file, whether compressed or not, is given a header that looks something like this:

	//This library: http://localhost/depender/build.php?requireLibs=mootools-core
	//Contents: Core, Hash, Number, Function, String, Array, (etc.)

From the header of the file you have the url needed to regenerate it as well as an inventory of the individual scripts included.

Requests and Query String Values
--------------------------------
To request a library, you can specify four arguments for the contents of the file:

* require - a comma separated list of *files* to require (`require=foo,bar`); can also be specified as `require=foo&require=bar`
* requireLibs - a comma separated list of *libraries* to require - these are the names defined the package names in each libary's package.yml or in the settings for those projects that use scripts.json. So, for example, *requireLibs=Core,More* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list or as `requireLibs=Core&requireLibs=More`).
* exclude - exactly like the `require` value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
* excludeLibs - just like the `exclude` option but instead you can specify entire libraries.

The Depender Client
-------------------
The Depender app includes a client side component that integrates with this server. It allows you to interact with the server in your application code, requiring components and executes a callback when the load. See [the docs for the client for details](client/Docs/Depender.Client.md).