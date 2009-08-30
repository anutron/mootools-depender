Depender: A MooTools Dependency Loader
======================================

This application generates concatenated libraries from multiple JavaScript files based on their dependencies and the files you require. It assumes that you have formatted your libraries in the way that MooTools is organized, though it does not require MooTools itself to operate.

Configuration
---------------
Included in this distribution is a file named "config_example.json" which, if copied to "config.json" will put this app into it's default mode. The values in the config.json are as follows:

* copyright - A string prepended to the beginning of all files built by the app. Defaults to the copyrights for the default libraries (MooTools Core & MooTools More)
* compression - The default compression to use. Values can be "yui", "jsmin", or "none" - defaults to "yui"; see compression section below for more details on compression.
* available_compressions - Supported compression types - defaults to both "yui", and "jsmin"; not all systems are set up to allow java executables at the command line (as on certain low-end hosting providers) so you may wish to disable yui.
* cache scripts.json - When *true* the app will cash the values in the scripts.json files in your libraries and improve performance. The down side is that if you change the scripts.json, you must refresh the cache by hitting */depender/build.php?reset=true*.
* libs - an object pointing to each library that the builder should support. Each entry has a setting for "scripts" which points to the directory that contains *scripts.json*. From the example file:

		"libs": {
			"mootools-core": {
				"scripts": "libs/core/Source"
			},
			"mootools-more": {
				"scripts": "libs/more/Source"
			}
		}

### Notes

* No two scripts in any of the libs should have the same name. So if one library has *Foo.js*, no other library should have a script with the same name. This is a remnant of the MooTools scripts.json, which wasn't designed originally to work with other scripts.json files. This naming requirement will be removed with MooTools 2.0.

Initialization
--------------
The application ships with two git submodule settings - one for the most recent, stable release of MooTools Core and another for MooTools More. Thought the application does not require these to function, most people will wish to include these. To initialize these libraries you must execute at the command line:

	git submodule update --init

This will download the libraries. Copy *config_example.json* over to *config.json* and the application is ready to run. If you do not have git installed on your computer, you can simply download the MooTools Core and MooTools More libraries and unzip them into *libs/core* and *libs/more*.

Note that the *outputs* directory must be writable by your web server.

Adding Libraries
----------------
Additional libraries can be easily added to the system by dropping their contents into the libs/ directory and editing the config file. You can use git submodules to track specific branches of external repositories or you can track a working branch using something like [crepo](http://github.com/cloudera/crepo/tree/master). Each library *must* have a *scripts.json* file that notes dependencies. I suggest the [Moo-ish Template](http://github.com/3n/mooish-template/tree/master) as a good place to start.

Compression
-----------
The application includes two compression libraries: [jsmin](http://www.crockford.com/javascript/jsmin.html) which is a native php library and [yui](http://developer.yahoo.com/yui/compressor/) which is a java command line utility. Whenever a library is built, the uncompressed version of the file is saved to disk. If compression is enabled or requested the file is run through the compressor and also written to disk.

Some systems may not be able to run the YUI compressor. For this purpose, there is another setting in the config file for "available_compressions" which is an array of the compressions you wish to support. It defaults to *[yui, jsmin]*. Setting this value to an empty array will disable compression support entirely.

Outputs
-------
Each requested file is output into it's own directory, named as the md5 hash of the file's contents (the list of file names, not the actual concatenated code). Each file, whether compressed or not, is given a header that looks something like this:

	//<copyright as defined in config.json>

	//Contents: Core, Hash, Number, Function, String, Array, etc.

	//This lib: http://localhost/depender/build.php?requireLibs=mootools-core

From the header of the file you have the url needed to regenerate it as well as an inventory of the individual scripts included.

In addition to these headers, each directory has a file entitled *contents.json* which has an object that lists the contents of the file. This file is not really intended to be used by you, but it may be helpful if you wish to integrate another system with the output.

Caching
-------
The setting in config.json for caching scripts.json controls whether the map of scripts is rebuilt on every request. Performance will improve if this is set to *false*, but the down side is any changes to scripts.json will not be reflected unless you clear the cache. This can be achieved by requesting */depender/build.php?reset=true*.

Requests and Query String Values
--------------------------------
To request a library, you can specify four arguments for the contents of the file:

* require - a comma separated list of *files* to require; can also be specified in the php style as "require[]=foo&require[]=bar"
* requireLibs - a comma separated list of *libraries* to require - these are the names defined in our *congfig.json* in the *libs* section. So, for example, *requireLibs=mootools-core,mootools-more* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list or the php style (*requireLibs[]=mootools-core&requireLibs[]=mootools-more*).
* exclude - exactly like the *require* value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
* excludeLibs - just like the *exclude* option but instead you can specify entire libraries.

### Additional Query String Values
In addition to the four values you can specify for the contents of the file, you can also override the default settings on the server for compression and caching. 

* cache - if set to *true* you'll be returned a cached version of the script even if the server is set to *false* and vice versa.
* compression - you'll be returned the compression type you specify regardless of the server default. Note that if you specify a compression type that the server does not allow, you'll be returned which ever one it does. If it does not support compression at all, you will not be returned a compressed file. You can also specify "none" which is useful for development and debugging.

The Depender Client
-------------------
MooTools More includes a client side component that integrates with this server. It allows you to interact with the server in your application code, requiring components and executes a callback when the load. See [the docs for the client for details](http://mootools.net/docs/more/Core/Depender.Client).


File System Caching vs Other Options
------------------------------------
Reading these files from the disk is not the best way to cache them. Every request still has to compute which items you need and check the local disk to see if the file exists. If it does php reads that file and sends it to the browser. There are other caching systems that are far more performant (such as [memcached](http://www.danga.com/memcached/) for example) that you may wish to consider. Unless you are using the system to lazy load content, you might consider downloading the built file and linking to it directly (just as if you'd downloaded it from [mootools.net](http://mootools.net) for example). For sites that do not have to support excessively large volumes of traffic you'll probably be fine just including the scripts directly from the builder (i.e. a script tag that links to "/depender/build.php?requireLibs=mootools-core").

The Builder Interface
=====================
The application ships with an HTML interface that allows you to pick and choose which files you wish to include in your download. You can easily specify your dependencies and see which files will be included with them. This interface basically just serves to help you construct the url for the library but also has a "Download" button to actually get the file if you want to save it. It can also be used to distribute your own plugins and files if you wish to share them.

