<?php

function yui($input){	
	exec("java -jar libraries/yuicompressor-2.3.5.jar --preserve-semi --line-break 150 --charset UTF-8 $input 2>&1", $out, $err);
	return $out;
}

?>