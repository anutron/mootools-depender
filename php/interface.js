var Interface = {
	start: function(){
		this.setupChex();
		this.setupActions();
		this.clippers();
		this.reset();
		this.setupHelp();
	},
	setupHelp: function(){
		var help_link = $('help_link').addEvent('click', this.showHelp.bind(this));
		$('close_help').addEvent('click', this.hideHelp.bind(this));
		var help = $('help');
		$(document.body).addEvent('click', function(e){
			if ($('help').getStyle('display') != "none") {
				var target = $(e.target);
				if (target != help && !help.hasChild(target) && target != help_link) this.hideHelp();
			}
		}.bind(this));
		$(document).addEvent('keydown', function(e){
			if (e.key == "esc") this.hideHelp();
		}.bind(this));
	},
	hideHelp: function(){
		if ($('help').getStyle('display') == "none") return;
		$('help').fade('out').get('tween').chain(function(){
			$('help').setStyle('display', 'none');
		});
	},
	showHelp: function(){
		if ($('help').getStyle('display') != "none") return;
		$('help').position({
			offset: {
				y: 50
			},
			position: "topcenter",
			edge: "topcenter"
		}).setStyles({
			opacity: 0,
			display: 'block'
		}).fade('in');
	},
	setupActions: function(){
		$('reset').addEvent('click', this.reset.bind(this));
		$('download').addEvent('click', function(){
			if (this.checkUrl()) window.location.href = this.getUrl() + '&download=true';
		}.bind(this));
	},
	clippers: function(){
		//TODO
		var copier = $('copier');
		var input = copier.getElement('input');
		var button = $('close_copier');
		button.addEvent('click', function(){
			copier.setStyle('display', 'none');
		});
		input.addEvent('focus', function(){
			input.select();
		});
		$('copy').addEvent('click', function(){
			if (this.checkUrl()) {
				input.set('value', this.getUrl());
				copier.setStyle('display', 'block').position();
				input.select();
			}
		}.bind(this));
		$('copy_scripts').addEvent('click', function(){
			if (this.checkUrl()) {
				input.set('value', '<scr'+'ipt src=\''+this.getUrl()+'\'></scr'+'ipt>');
				copier.setStyle('display', 'block').position();
				input.select();
			}
		}.bind(this));
	},
	getUrl: function(){
		var form = document.getElement('form');
		var uri = new URI(form.get('action'));
		uri.set('query', form.toQueryString());
		return uri.toString();
	},
	checkUrl: function(){
		var uri = new URI(this.getUrl());
		if (!uri.get('data').require && !uri.get('data').requireLibs) {
			$('warn_url').position().setStyle('display', 'block').fade('in').get('tween').clearChain().chain(function(){
				(function(){
					$('warn_url').fade('out').get('tween').chain(function(){
						$('warn_url').setStyle('display', 'block');
					});
				}).delay(1500);
			});
			return false;
		}
		return true;
	},
	reset: function(){
		$$('div.includes input').set('checked', false);
		$$('li').each(function(li){
			li.removeClass('required').removeClass('checked').removeClass('excluded');
		});
		$$('dd.sourceContents').setStyle('display', 'block');
		$$('dt.sourceHeader span').removeClass('selected');
	},
	setupChex: function() {
		this.scripts = $$('li.script');
		this.scripts.each(function(script){
			var input = script.getElement('input');
			script.store('input', input);
			input.store('li', script);
		}, this);
		$(document.body).addEvent('click:relay(li.script)', this.select.bind(this));

		this.excludes = $$('li.exclude');
		this.excludes.each(function(ex, i) {
			var input = ex.getElement('input');
			ex.store('input', input);
			ex.store('script', this.scripts[i]);
			input.store('li', ex);
		}, this);
		$(document.body).addEvent('click:relay(li.exclude)', this.toggleExclude.bind(this));
		
		var sections = $$('dd.sourceContents');
		$$('dt.sourceHeader').each(function(header, i){
			header.store('section', sections[i]);
			sections[i].store('header', header);
			var all = header.getElement('.sourceAll');
			var none = header.getElement('.sourceNone');
			all.store('other', none);
			none.store('other', all);
			[all, none].each(function(button) {
				button.addEvent('click', this.selectSource.bind(this));
				button.store('input', button.getElement('input')).store('section', sections[i]);
			}, this);
		}, this);
	},

	selectSource: function(e){
		var input = $(e.target).retrieve('input');
		var section = $(e.target).retrieve('section');
		if (input.get('checked')) {
			$(e.target).removeClass('selected');
			input.set('checked', false);
			section.reveal().get('reveal').chain(function(){
				section.getElements('input').each(function(input) {
					input.removeClass('libincluded').removeClass('libexcluded');
				});
				this.compute();
			}.bind(this));
		} else {
			$(e.target).addClass('selected').getElement('input').set('checked', true);;
			$(e.target).retrieve('other').removeClass('selected').getElement('input').set('checked', false);
			input.set('checked', true);
			section.dissolve().get('reveal').chain(function(){
				this.resetSection(section);
				var state = input.get('name') == 'requireLibs' ? 'libincluded' : 'libexcluded';
				section.getElements('input').addClass(state);
				this.compute();
			}.bind(this));
		}
	},

	resetSection: function(section) {
		section.getElements('li').each(function(li){
			li.removeClass('excluded').removeClass('checked').removeClass('required');
			li.retrieve('input').set('checked', false);
		});
	},
	
	excludeLibrary: function(e, target){
		$(target).retrieve('section').dissolve().get('reveal').chain(this.compute.bind(this));
		$(target).getElement('input').set('checked', true);
	},
	
	select: function(e, target) {
		var input = $(target).retrieve('input');
		if (input.get('checked')) this.uncheck(input);
		else this.check(input);
	},
	check: function(input){
		input.set('checked', true);
		input.retrieve('li').addClass('checked');
		this.compute();
	},
	uncheck: function(input) {
		input.set('checked', false);
		input.retrieve('li').removeClass('checked');
		this.compute();
	},
	getDeps: function(script, reqs){
		reqs = reqs || [];
		if (script == 'None' || !script || $(script).hasClass('libexcluded')) return reqs;
		script = $(script);
		var deps = script.get('deps')?script.get('deps').split(',') : [];
		var id = script.get('id');
		deps.each(function(scr){
			if (scr == id || scr == 'None' || !scr) return;
			if (!reqs.contains(scr)) reqs.combine(this.getDeps(scr));
			reqs.include(scr);
		}, this);
		return reqs;
	},
	compute: function() {
		var deps = [];
		this.scripts.each(function(script){
			var input = script.retrieve('input');
			if (!input.get('checked') && !input.hasClass('libincluded')) return;
			var ret = this.getDeps(input, deps);
			deps.combine(ret);
		}, this);
		this.scripts.each(function(script){
			var input = script.retrieve('input');
			if (deps.contains(input.get('id'))) script.addClass('required');
			else script.removeClass('required');
		});
	},
	toggleExclude: function(e, target){
		var input = $(target).retrieve('input');
		if (input.get('checked')) this.unexclude(input);
		else this.exclude(input);
	},
	exclude: function(input) {
		input.set('checked', true);
		var ex = input.retrieve('li').addClass('excluded');
		ex.retrieve('script').addClass('excluded');
	},
	unexclude: function(input) {
		input.set('checked', false);
		var ex = input.retrieve('li').removeClass('excluded');
		ex.retrieve('script').removeClass('excluded');
	}
};
window.addEvent('domready', function(){
	document.addEvent('click', function(e) {
		var copier = $('copier');
		if (e.target != copier && !copier.hasChild(e.target) && e.target != $('copy') && e.target != $('copy_scripts')) copier.setStyle('display', 'none');
	});
	document.addEvent('keyup', function(e) {
		if (e.key == "esc") $('copier').setStyle('display', 'none');
	});
});