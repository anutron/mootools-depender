<?php

include_once 'compressors/jsmin-1.1.1.php';

function jsmin($script){
	return JSMin::minify($script);
}

?>