<?php
include_once 'depender.php';

if (!file_exists('cache')) mkdir('cache');
$depender = New Depender;
if ($depender->getVar('require') || $depender->getVar('requireLibs') || $depender->getVar('client')) {
	$depender->build();
} else if ($depender->getVar('reset')) {
	$depender->deleteCache('flat');
}

