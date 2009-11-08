<?php
include_once "build.php";
$depender = New Depender;
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<title>Depender - A MooTools Dependency Builder</title>
		<link rel="stylesheet" href="../styles/reset.css" type="text/css" media="screen" title="no title" charset="utf-8">
		<link rel="stylesheet" href="../styles/depender.css" type="text/css" media="screen" title="no title" charset="utf-8">
		<script src="build.php?requireLibs=mootools-core&require=Fx.Reveal,URI,Element.Position,String.QueryString,Element.Delegation"></script>
		<script src="interface.js" type="text/javascript" charset="utf-8"></script>
	</head>
	<body>
		<h1>
			MooTools Library Builder
			<a class="button" id="help_link">Help</a>
		</h1>
		<?php include_once "builder.form.php"; ?>

		<script>
			window.addEvent('domready', function(){
				Interface.start();
				$('help').position();
			});
		</script>

	</body>
</html>