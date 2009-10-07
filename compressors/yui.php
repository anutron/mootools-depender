<?php

function yui($input, $path, $root){
	$file = $root."compressors/yuicompressor-2.4.2.jar";
	if (!file_exists($file)) die('Could not load file: '.$file);
	if (!file_exists($path)) die('Could not load file: '.$path);
	exec("java -jar ".$file." --preserve-semi -v --line-break 150 --charset UTF-8 ".$path."", $out, $err);
	return join($out, PHP_EOL);
}

?>