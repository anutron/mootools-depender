<?php

function jsmin($script, $path, $root){
	include_once $root.'compressors/jsmin-1.1.1.php';
	return JSMin::minify($script);
}

?>