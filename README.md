Depender: A MooTools Dependency Loader
======================================

This application generates concatenated libraries from multiple JavaScript files based on their dependencies and the files you require. It assumes that you have formatted your libraries in the way that MooTools is organized, though it does not require MooTools itself to operate.

Overview
-------

This is the official library builder for MooTools libraries. While this application can be used without MooTools to build libraries from other sources, it makes use of certain conventions tied to the MooTools JavaScript library and the manner in which its files are organized. In particular, the use of a file called *scripts.json* that describes the locations of scripts and their dependencies.

The purpose of this application is to allow users to build their own libraries using MooTools files and files of their own. It can, if you choose, be used in a live environment to deliver scripts on the fly, but this is not its recommended use. It's more appropriate, especially for high-traffic applications, to use this application to output libraries and save these for deployment as static files. Linking to the application directly may produce a demand on server resources that is not acceptable.

Included in this distribution is a PHP version of the builder and a Django/Python version. Additionally, there is a client library - Depender.Client.js - that allows for interactive, lazy-loading of required libraries. Using this client requires that you pull scripts from the Depender server, which depending on the load of your application, may not be acceptable.

Installation
------------

This application comes in two forms: a PHP version and a Django/Python version. Each has advantages and disadvantages.

The PHP version of the application is very easy to deploy (just drop it into a directory in your webserver's htdocs and hit it with your browser). It also ships with a download builder interface that allows you to view the files available, click the dependencies you require and download the library. However, the PHP version is less performant than the Django version, and if you plan on deploying this server for applications to pull JavaScript from it, you should consider using the Django app. See the information on Caching below for more details on the PHP version's performance.

**NOTE: The depender/php/cache directory MUST be writable by your web app**

The Django app does not have an html builder like the PHP version, but it's caching system is far more robust as it stores all scripts in memory. It is also easy to deploy assuming your server has Python running. Simply extract the files from this application onto your server and run "python manage.py runserver".

Configuration
---------------
Included in this distribution is a file named "config_example.json" which, if copied to "config.json" will put this app into its default mode. The values in the config.json are as follows:

* compression - The default compression to use. Values can be "yui", "jsmin", or "none" - defaults to "none"; see compression section below for more details on compression.
* available_compressions - Supported compression types - defaults to both "yui", and "jsmin"; not all systems are set up to allow java executables at the command line (as on certain low-end hosting providers) so you may wish to disable yui. The Django app only supports yui (and none); it ignores any other listed types - so it will ignore jsmin for example.
* libs - an object pointing to each library that the builder should support. Each entry has a setting for "scripts" which points to the directory that contains *scripts.json*. From the example file:

		"libs": {
			"mootools-core": {
				"copyright": "//MooTools, <http://mootools.net>, My Object Oriented (JavaScript) Tools. Copyright (c) 2006-2009 Valerio Proietti, <http://mad4milk.net>, MIT Style License."
				"scripts": "libs/core/Source"
			},
			"mootools-more": {
				"copyright": "//MooTools More, <http://mootools.net/more>. Copyright (c) 2006-2009 Aaron Newton <http://clientcide.com/>, Valerio Proietti <http://mad4milk.net> & the MooTools team <http://mootools.net/developers>, MIT Style License.",
				"scripts": "libs/more/Source"
			}
		}

* php: cache scripts.json - When *true* the app will cash the values in the scripts.json files in your libraries and improve performance. The down side is that if you change the scripts.json, you must refresh the cache by hitting */depender/build.php?reset=true*. Note that **this value only applies to the php version** of this application, not the django version.

### Notes

* No two scripts in any of the libs should have the same name. So if one library has *Foo.js*, no other library should have a script with the same name. This is a remnant of the MooTools scripts.json, which wasn't designed originally to work with other scripts.json files. This naming requirement will be removed with MooTools 2.0.
* The copyrights will be included in the header of each library.

Initialization
--------------
The application ships with two git submodule settings - one for the most recent, stable release of MooTools Core and another for MooTools More. Though the application does not require these to function, most people will wish to include these. To initialize these libraries you must execute at the command line:

	git submodule update --init

This will download the libraries. Copy *config_example.json* over to *config.json* and the application is ready to run. If you do not have git installed on your computer, you can simply download the MooTools Core and MooTools More libraries and unzip them into *libs/core* and *libs/more*.

Note that the *php/cache* directory must be writable by your web server if you are using the PHP version of the library.

### Django Settings
The Django application includes a *settings.py* file that has additional settings:

DEPENDER_ROOT - the path to the root of the extracted files (where this README resides); you shouldn't need to alter this.
DEPENDER_CONFIG_JSON - the path to *config.json*; if you copy *config_example.json* to *config.json* this shouldn't need altering.
DEPENDER_YUI_PATH - the path to the YUI compressor; you shouldn't need to alter this.
DEPENDER_DEBUG - if *True* depender does not catch or compress results, regardless of other configuration. This is useful for development.

Adding Libraries
----------------
Additional libraries can be easily added to the system by dropping their contents into the libs/ directory and editing the config file (they do not have to reside in the libs/ directory; so long as the config points to the appropriate location). You can use git submodules to track specific branches of external repositories or you can track a working branch using something like [crepo](http://github.com/cloudera/crepo/tree/master). Each library *must* have a *scripts.json* file that notes dependencies. I suggest the [Moo-ish Template](http://github.com/3n/mooish-template/tree/master) as a good place to start.

Compression
-----------

### PHP Compression

The application includes two compression libraries: [jsmin](http://www.crockford.com/javascript/jsmin.html) which is a native php library and [yui](http://developer.yahoo.com/yui/compressor/) which is a java command line utility. Whenever a library is built, the uncompressed version of the file is saved to disk. If compression is enabled or requested the file is run through the compressor and also written to disk.

Some systems may not be able to run the YUI compressor. For this purpose, there is another setting in the config file for "available_compressions" which is an array of the compressions you wish to support. It defaults to *[yui, jsmin]*. Setting this value to an empty array will disable compression support entirely.

### Django/Python Compression

The Django application also makes use of the YUI compressor. Unlike the PHP version, it doesn't cache results to disk but rather to memory, which makes it much faster and more ideal for actual deployment. Also unlike the PHP version, the Django version compresses *every* file the first time you hit it. Thus, the first request when the application starts up can take quite a while. After this, the application is very fast. Note that if you change files on the disk, the application will not pick up these changes until you restart it (unless you are in debug mode; see the section on Django Settings above).

Headers and Output
-------
Each file, whether compressed or not, is given a header that looks something like this:

	//<copyright as defined in config.json>

	//Contents: Core, Hash, Number, Function, String, Array, etc.

	//This lib: http://localhost/depender/build.php?requireLibs=mootools-core

From the header of the file you have the url needed to regenerate it as well as an inventory of the individual scripts included.

Requests and Query String Values
--------------------------------
To request a library, you can specify four arguments for the contents of the file:

* require - a comma separated list of *files* to require; can also be specified in the php style as "require[]=foo&require[]=bar"
* requireLibs - a comma separated list of *libraries* to require - these are the names defined in our *congfig.json* in the *libs* section. So, for example, *requireLibs=mootools-core,mootools-more* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list or the php style (*requireLibs[]=mootools-core&requireLibs[]=mootools-more*).
* exclude - exactly like the *require* value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
* excludeLibs - just like the *exclude* option but instead you can specify entire libraries.

### Additional Query String Values
In addition to the four values you can specify for the contents of the file, you can also override the default settings on the server for compression and caching. 

* compression - you'll be returned the compression type you specify regardless of the server default. Note that if you specify a compression type that the server does not allow, you'll be returned which ever one it does. If it does not support compression at all, you will not be returned a compressed file. You can also specify "none" which is useful for development and debugging.
* reset - if true, destroys the cache and rebuilds it. Note that this represents an expense when compression is enabled.

The Depender Client
-------------------
The Depender app includes a client side component that integrates with this server. It allows you to interact with the server in your application code, requiring components and executes a callback when the load. See [the docs for the client for details](client/Docs/Depender.Client.md).

File System Caching vs Other Options
------------------------------------
As noted above, the PHP version of this application caches files to disk. Reading these files from the disk is not the best way to cache them. Every request still has to compute which items you need and check the local disk to see if the file exists. If it does php reads that file and sends it to the browser. There are other caching systems that are far more performant (such as [memcached](http://www.danga.com/memcached/) for example) that you may wish to consider. Unless you are using the system to lazy load content, you might consider downloading the built file and linking to it directly (just as if you'd downloaded it from [mootools.net](http://mootools.net) for example). For sites that do not have to support excessively large volumes of traffic you'll probably be fine just including the scripts directly from the builder (i.e. a script tag that links to "/depender/build.php?requireLibs=mootools-core"). The Django version of the application caches to memory and is much faster and more suited for live deployment.

The Builder Interface
---------------------
The PHP application ships with an HTML interface that allows you to pick and choose which files you wish to include in your download. You can easily specify your dependencies and see which files will be included with them. This interface basically just serves to help you construct the url for the library but also has a "Download" button to actually get the file if you want to save it. It can also be used to distribute your own plugins and files if you wish to share them.

