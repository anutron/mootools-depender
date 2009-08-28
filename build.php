<?php

Class Depender {
	const ConfigFilename  = 'config.json';
	const ScriptsFilename = 'scripts.json';

	const Post            = 'POST';
	const Get             = 'GET';

	const Yui             = 'yui';
	const JSMin           = 'jsmin';

	public function getConfig() {
		return json_decode( file_get_contents( self::ConfigFilename ), True );
	}

	public function getLibraries() {
		$all      = Array();
		$config  = $this->getConfig();
		foreach($config['libs'] as $libraryName => $library) {
			$scripts           = $this->getScriptsFromLibraryName($libraryName);
			$all[$libraryName] = $scripts;
		}
		return $all;
	}

	private function getScriptsFromLibraryName($name) {
		$config  = $this->getConfig();
		$library = $config['libs'][$name];
		return json_decode(file_get_contents($library['scripts'].'/'.self::ScriptsFilename), True);
	}

	private function getScriptsNamesFromLibrary($library) {
		$all = Array();
		foreach($library as $categoryName => $scripts) {
			foreach($scripts as $scriptName => $script) {
				$all[] = $scriptName;
			}
		}
		return $all;
	}

	public function getCompressions() {
		$config = $this->getConfig();
		return $config['available_compressions'];
	}

	public function getDefaultCompression() {
		$config = $this->getConfig();
		return $config['compression'];
	}

	public function getVar($name, $default = False) {
		switch ($_SERVER['REQUEST_METHOD']) {
			case self::Post:
				$var = $_POST[$name];
				break;
			case self::Get:
				$var = $_GET[$name];
				break;
		}

		if ( !$var ) {
			return $default;
		}
		return $var;
	}

	private function getFlatData() {
		$config  = $this->getConfig();
		$flat    = Array();
		$all     = Array();
		$cacheId = 'flat';
		$cached  = $this->getCache($cacheId);
		if ($cached) {
			return $cached;
		}
		foreach($config['libs'] as $libraryName => $library) {
			$scripts = $this->getScriptsFromLibraryName($libraryName);

			foreach($scripts as $categoryName => $categotyScripts) {

				foreach($categotyScripts as $scriptName => $script) {
					$script['library']  = $libraryName;
					$script['category'] = $categoryName;
					$script['name']     = $scriptName;
					$script['path']     = $library['scripts'].'/'.$script['category'].'/'.$script['name'].'.js';
					$all[$scriptName]   = $script;
				}
			}
		}
		$this->setCache($cacheId, $all);
		return $all;
	}

	private function getDependencies($script) {
		$scripts = $this->getFlatData();
		$deps = $scripts[$script]['deps'];
		if (is_array($deps)) {
			return $deps;
		} else {
			return Array();
		}
	}

	private function getScriptFile($scriptName, $compression=False) {
		$flat      = $this->getFlatData();
		$script    = $flat[$scriptName];
		if (!is_array($script)) {
			return '';
		}

		$atime     = fileatime($script['path']);
		$cacheId   = $script['name'].'_'.$atime.'_'.$compression;
		$cached    = $this->getCache($cacheId);
		if ($cached) {
			return $cached;
		}

		$contents  = file_get_contents($script['path']);

		if ($compression) {
			$contents = $this->compress($contents, $compression);
		}
		$this->setCache($cacheId, $contents);
		return $contents;
	}

	public function compress($string, $compression) {
		include_once('compressors/'.$compression.'.php');
		$compressed = call_user_func_array($compression, array($string));
		return $compressed;
	}

	public function header() {
		header('Cache-Control: must-revalidate');
		if ($this->getVar('download')) {
			header('Content-Disposition: attachment; filename="built.js"');
		} else {
			header("Content-Type: application/x-javascript");
		}
	}

	private function getPageUrl() {
		$pageURL = 'http';
		if (isset($_SERVER["HTTPS"]) && $_SERVER["HTTPS"]) {$pageURL .= "s";}
		$pageURL .= "://";
		if ($_SERVER["SERVER_PORT"] != "80") {
			$pageURL .= $_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$_SERVER["REQUEST_URI"];
		} else {
			$pageURL .= $_SERVER["SERVER_NAME"].$_SERVER["REQUEST_URI"];
		}
		return str_replace('&download=true', '', $pageURL);
	}

	private function setCache($id, $value) {
		$file = fopen('cache/'.$id, 'w+') or die("can't open file: cache/".$id);
		$result = fwrite($file, serialize($value));
		fclose($file);
		return $result;
	}

	private function getCache($id) {
		$file = 'cache/'.$id;
		if (file_exists($file)) {
			return unserialize(file_get_contents($file));
		} else {
			return False;
		}
	}

	private function deleteCache($id) {
		$file = 'cache/'.$id;
		if (file_exists($file)) {
			return unlink($file);
		}
	}

	private function getLastModifiedDate($scripts) {
		$max  = 0;
		$flat = $this->getFlatData();
		foreach($scripts as $scriptName) {
			$script   = $flat[$scriptName];
			$modified = fileatime($script['path']);
			if ($modified > $max) {
				$max = $modified;
			}
		}
		return $max;
	}

	public function build() {
		$include     = $this->getVar('require') ? explode(',', $this->getVar('require')) : Array();
		$exclude     = $this->getVar('exclude') ? explode(',', $this->getVar('exclude')) : Array();

		$includeLibs = $this->getVar('requireLibs') ? explode(',', $this->getVar('requireLibs')) : Array();
		$excludeLibs = $this->getVar('excludeLibs') ? explode(',', $this->getVar('excludeLibs')) : Array();

		$this->header();

		$libs        = $this->getLibraries();
		$includes    = Array();
		$excludes    = Array();
		$config      = $this->getConfig();
		$out         = join($config['copyright'], PHP_EOL).PHP_EOL.PHP_EOL;
		$out        .= '//This lib: '.$this->getPageUrl().PHP_EOL.PHP_EOL;

		foreach($includeLibs as $includeLib) {
			$library  = $libs[$includeLib];
			foreach($this->getScriptsNamesFromLibrary($library) as $script) {
				$includes   = array_merge($includes, $this->getDependencies($script));
				$includes[] = $script;
			}
		}

		foreach($include as $script) {
			$includes   = array_merge($includes, $this->getDependencies($script));
			$includes[] = $script;
		}
		$includes = array_unique($includes); //No duplicate

		foreach($excludeLibs as $excludeLib) {
			$library  = $libs[$excludeLib];
			$excludes = array_merge($excludes, $this->getScriptsNamesFromLibrary($library));
		}

		foreach($exclude as $script) {
			$excludes[] = $script;
		}
		$excludes = array_unique($excludes); //No duplicate

		$includes = array_diff($includes, $excludes);


		if ($_SERVER['HTTP_IF_MODIFIED_SINCE']) {
			$browserCache = strtotime($_SERVER['HTTP_IF_MODIFIED_SINCE']);
			if ($browserCache >= $this->getLastModifiedDate($includes)) {
				header('HTTP/1.1 304 Not Modified');
				exit;
			}
		}

		header('Last-modified: '.date('r', $this->getLastModifiedDate($includes)));

		foreach($includes as $include) {
			$out .= $this->getScriptFile($include, $this->getVar('compression'));
		}

		print $out;
	}
}

$depender = New Depender;
if ($depender->getVar('require') || $depender->getVar('requireLibs')) {
	$depender->build();
}
?>