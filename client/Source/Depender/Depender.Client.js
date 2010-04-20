// Copyright (c) 2010, Cloudera, inc. All rights reserved.
/*
---
description: A dependency loader for the MooTools library that integrates with <a
  href="http://github.com/anutron/mootools-depender/tree/">the server side Depender
  library</a>.
provides: [Depender.Client]
requires: [Core/Class.Extras, Core/Element.Event]
script: Depender.Client.js
authors: [Aaron Newton]

...
*/

var Depender = {

	options: {
		/* 
		onRequire: $empty(options),
		onRequirementLoaded: $empty([scripts, options]),
		target: null,
		builder: '/depender/build.php'
		*/
	},
	
	loadedSources: [],

	loaded: [],
	
	required: [],

	finished: [],
	
	lastLoaded: 0,

	require: function(options){
		if (!this.options.builder) return;
		this.fireEvent('require', options);

		var finish = function(script){
			this.finished.push(script);
			if (options.callback) {
				if (options.domready) window.addEvent('domready', options.callback.pass(options));
				else options.callback(options);
			}
			this.fireEvent('scriptLoaded', {
				script: this.loaded.join(', '),
				totalLoaded: (this.finished.length / this.required.length * 100).round(),
				currentLoaded: ((this.finished.length - this.lastLoaded) / (this.required.length - this.lastLoaded) * 100).round(),
				loaded: this.loaded
			});
			if (this.required.length == this.finished.length) this.lastLoaded = this.finished.length;
			this.fireEvent('requirementLoaded', [this.loaded, options]);
		}.bind(this);

		var src = [this.options.builder + '?client=true'];
		
		if (options.compression) src.push('compression=' + options.compression);

		if (options.scripts) {
			var scripts = $splat(options.scripts).filter(function(script) {
				return !this.loaded.contains(script);
			}, this);
			if (scripts.length) src.push('require=' + scripts.join(','));
		}

		if (options.sources) {
			var sources = $splat(options.sources).filter(function(source){
				return !this.loadedSources.contains(source);
			}, this);
			if (sources.length) src.push('requireLibs=' + $splat(sources).join(','));
		}

		if (src.length == 1) {
			finish();
			return this;
		}

		if (this.loaded.length) {
			src.push('exclude=' + this.loaded.join(','));
		}
		var finished;
		var script = new Element('script', {
			src: src.join('&'),
			events: {
				readystatechange: function(){
					if (['loaded', 'complete'].contains(this.readyState) && !finished) {
						finished = true;
						finish(script);
					}
				},
				load: function(){
					if (!finished) {
						finished = true;
						finish(script);
					}
				}
			}
		}).inject(this.options.target || document.head);

		this.required.push(script);

		return this;

	}

};

//make it easy to switch between the server side and the client side versions of this library.
['enableLog', 'disableLog', 'include'].each(function(fn) {
	Depender[fn] = $lambda(Depender);
});

$extend(Depender, new Events);
$extend(Depender, new Options);
