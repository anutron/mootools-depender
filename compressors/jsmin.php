<?php

include_once 'libraries/jsmin-1.1.1.php';

function jsmin($script){
	return JSMin::minify($script);
}

?>