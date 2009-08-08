<?php

function lg($str) {
	echo $str."<br/>";
}
function encode($val){
	return json_encode($val);
}
function decode($string){
	return json_decode($string, true);
}
function readJson($string){
	if (file_exists($string)) {
		return decode(file_get_contents($string));
	}
}
$conf = readJson("config.json");
$sources = array();
function getScripts(){
	global $conf, $sources;
	$data = array();
	foreach($conf["libs"] as $source => $props){
		$sources[$source] = readJson($props["scripts"]."/scripts.json");
		foreach($sources[$source] as $dir => $files) {
			foreach($files as $file => $fileprops) {
				$data[$file] = array();
				$data[$file]["path"] = $props["scripts"]."/".$dir."/".$file.".js";
				$data[$file]["deps"] = $fileprops["deps"];
			}
		}
	}
	return $data;
}
$scriptMap = getScripts();

function merge_unique($ar1, $ar2) {
	foreach($ar1 as $var) {
		if (!in_array($var, $ar2)) array_push($ar2, $var);
	}
	return $ar2;
}
function computeDependencies($scripts, $data){
	if (!is_array($scripts)) $scripts = array($scripts);
	$deps = array();
	foreach($scripts as $script) {
		foreach($data[$script]["deps"] as $dep) {
			if (!in_array($dep, $scripts)) $deps = merge_unique($deps, computeDependencies($dep, $data));
		}
		if (!in_array($script, $deps)) { array_push($deps, $script); }
	}
	return $deps;
}
function curPageURL() {
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

function build() {
	global $conf, $scriptMap, $sources;
	$require = array();
	$exclude = array();
	if (getVar('requireLibs')) {
		$requireLibs = getVar('requireLibs');
		if (!is_array($requireLibs)) $requireLibs = array($requireLibs);
		foreach($requireLibs as $lib) {
			foreach($sources[$lib] as $dir => $files) {
				foreach($files as $file => $fileprops) {
					$require[] = $file;
				}
			}
		}
	}
	if (getVar('excludeLibs')) {
		$excludeLibs = getVar('excludeLibs');
		if (!is_array($excludeLibs)) $excludeLibs = array($excludeLibs);
		foreach($excludeLibs as $lib) {
			foreach($sources[$lib] as $dir => $files) {
				foreach($files as $file => $fileprops) {
					$exclude[] = $file;
				}
			}
		}
	}
	
	$reqs = getVar('require');
	if ($reqs) {
		if (!is_array($reqs)) $reqs = split(',',$reqs);
		$require = merge_unique($reqs, $require);
	}
	$exs = getVar('exclude');
	if ($exs) {
		if (!is_array($exs)) $exs = split(',',$exs);
		$exclude = merge_unique($exs, $exclude);
	}
	
	$cache = ($conf["cache"] == "true");
	if (getVar('noCache')) $cache = false;
	$compression = $conf["compression"];
	if (getVar('compression')) $compression = getVar('compression');
	
	$deps = computeDependencies($require, $scriptMap);
	$output = array();
	$output_contents = array();
	$paths = array();
	
	foreach($deps as $dep) {
		if (!in_array($dep, $exclude) && file_exists($scriptMap[$dep]["path"])) $output_contents[] = $dep;
	}

	$dirName = 'outputs/'.md5(join($output_contents, '-'));
	$fileName = $dirName.'/'.'script';
	$uncompressed = $fileName.'_uncompressed.js';
	header("Content-Type: application/x-javascript");
	if (getVar('download')) header('Content-Disposition: attachment; filename="built.js"');

	switch($compression) {
		case 'yui':
			$fileName = $fileName.'_yui_compressed.js';
			break;
		case 'jsmin':
			$fileName = $fileName.'_jsmin_compressed.js';
			break;
		case 'none':
			$fileName = $fileName.'_uncompressed.js';
			break;
	}
	if (file_exists($fileName) && $cache) {
		$responseName = join($require, '-').'.js';
		header('filename="'.$responseName.'"');
		echo file_get_contents($fileName);
		return;
	}

	foreach($output_contents as $dep) {
		$output[] = file_get_contents($scriptMap[$dep]["path"]);
	}

	if (count($output_contents) > 0) {
		if (!is_dir($dirName)) mkdir($dirName);
		$breaks = PHP_EOL.PHP_EOL;
		$header = join($conf["copyright"], $breaks).$breaks."//Contents: ".join($output_contents,', ').$breaks;
		$header = $header.'//This lib: '.curPageURL().$breaks;

		$build = join($output, $breaks);
		
		writeFile('{ "contents": '.encode($output_contents).'}', $dirName.'/contents.json');
		
		writeFile($header.$build, $uncompressed);

		if ($compression != "none") {
			if ($compression == "yui") {
				$build = join(compress_yui($uncompressed), PHP_EOL);
				writeFile($header.$build, $fileName);
			}
			if ($compression == "jsmin") {
				$build = compress_jsmin($build);
				writeFile($header.$build, $fileName);
			}
		}
		$responseName = join($require, '-').'.js';
	} else {
		$responseName = "empty.js";
		$header = "";
		$build = "";
	}
	header('filename="'.$responseName.'"');
	echo $header.$build;

}

function compress_yui($input){
	loadLib('yui');
	return yui($input);
}

function compress_jsmin($build){
	loadLib('jsmin');
	return jsmin($build);
}

function writeFile($output, $name) {
	$fh = fopen($name, 'w') or die("can't open file");
	fwrite($fh, $output);
	fclose($fh);
}
function loadLib($lib) {
	$file = "libraries/$lib.php";
	if (file_exists($file)){
		include_once $file;
		return true;
	}
	return false;
}
//build("Array", "Core");
function getVar($var) {
	switch($_SERVER['REQUEST_METHOD']) {
		case 'GET': $the_request = &$_GET; break;
		case 'POST': $the_request = &$_POST; break;
	}
	if (isset($the_request[$var])) return $the_request[$var];
	return false;
}
if (strpos($_SERVER["REQUEST_URI"], 'build.php')) {
	if (getVar('require') || getVar('requireLibs')) {
		build();
	} else {
		header("Content-Type: application/x-javascript");
		echo "//No scripts specified";
	}
}
?>