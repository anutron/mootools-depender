<?php 
	$conf = $depender->getConfig();
?>
<form action="build.php" method="GET">
	<div class="includes">
		<dl class="sources">
		<?php 
				foreach ($depender->getLibraries() as $source => $data) {
					if ($source != "depender-client") { ?>
			<dt class="sourceHeader">
				<div class="select">
					<span class="button sourceAll">include entire library
						<input type="checkbox" value="<?php echo $source ?>" name="requireLibs[]">
					</span>
					<span class="button sourceNone">exclude entire library
						<input type="checkbox" value="<?php echo $source ?>" name="excludeLibs[]">
					</span>
				</div>
				<?php echo $conf["libs"][$source]["name"].": ".$conf["libs"][$source]["version"]; ?>
			</dt>
			<dd class="sourceContents">
				<dl class="dirs">
				<?php foreach($data as $dir => $scripts) {?>
					<dt class="dirHeader"><?php echo $dir ?></dt>
					<dd class="dirContents">
						<ul class="scripts clearfix">
						<?php foreach($scripts as $script => $details) {?>
							<li class="script">
								<b class="scriptName">
									<?php echo $script ?>
								</b>
								<?php if (isset($details["desc"])) {?>
									<div class="description"><?php echo $details["desc"]; ?></div>
								<?php } ?>
								<input type="checkbox" name="require[]" value="<?php echo $script ?>"
								 	id="<?php echo $script ?>" 
									deps="<?php echo join($details["deps"], ','); ?>"/>
							</li>
							<li class="exclude">
								<input type="checkbox" name="exclude[]" value="<?php echo $script ?>"/>
								exclude
							</li>
						<?php } ?>
						</ul>
					</dd>
				<?php } ?>
				</dl>
			</dd>
		<?php	} 
			} ?>
		</dl>
	</div>
<div id="controls">	
	<table cellpadding="0" cellspacing="0" border="0">
		<thead>
			<tr>
				<th id="compression" colspan="3">compression: </th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td id="compression_container">
					<ul>
						<?php foreach($depender->getCompressions() as $comp) { ?>
						<li><label>
							<input type="radio" name="compression" value="<?php echo $comp.'" '; if ( $comp === $depender->getDefaultCompression()) echo 'checked="checked"';?>/>
							<?php echo $comp; ?></label>
						</li>
						<?php } ?>
						<li><label>
							<input type="radio" name="compression" value=""/>
							none</label>
						</li>
					</ul>
				</td>
				<td id="client">
					integrate depender client:
					<input type="checkbox" name="client" value="true"/>
				</td>
				<td id="action_list">
					<ul>
						<li><a id="reset" class="button">Reset</a></li>
						<li><a id="download" class="button">Download</a></li>
						<li><a id="copy" class="button">Copy URL</a></li>
						<li><a id="copy_scripts" class="button">Copy &lt;script&gt;</a></li>
					</ul>
				</td>
			</tr>
		</tbody>
	</table>
</div>
</form>
<div id="help">
	<h2>Interface Usage
		<a id="close_help" class="button">close</a>
	</h2>
	<div id="help_contents">
		<h3>Step 1</h3>
		<p>Select the files you need for your application. You can select as many as you like. <b class="green">Green</b> items in the list are files that will be included in your download - these are dependencies of the files you select. You may, if you like, include entire libraries by selecting that option in the header for each library you wish to include.</p>
		<h3>Step 2</h3>
		<p>Select any files or libraries you wish to exclude. This is useful if a portion of your application has already been loaded. For example, if you load MooTools Core through the <a href="http://code.google.com/apis/ajaxlibs/documentation/index.html#mootools">Google Ajax Libraries API</a>, and you want to include a plugin from <a href="http://mootools.net/more">MooTools More</a> you can select the files you want and exclude MooTools Core, which you already have.</p>
		<h3>Step 3</h3>
		<p>Choose what compression you want for your file. The default is noted and if you make no selection this default will be used. Note that if you do not specify a compression and later the server changes configuration, scripts included directly from the builder will switch to the compression configured at that time.</p>
		<h3>Step 4</h3>
		<p>To get your library, you can download the file directly by clicking "Download." You can, alternately, copy the url to the file or copy the script tag for the url. This will pull the build library from the builder every time it is requested. If caching is enabled compressed libraries will be cached (to disk) to improve performance. Sites with high performance needs will likely want to implement a more robust caching system such as <a href="http://www.danga.com/memcached/">memcached</a>.</p>
		<h3>Output</h3>
		<p>Scripts output by this library include in their header comments a list of all files they include as well as a url that can be used to recreate them.</p>
		<h3>Configuration</h3>
		<p>See <a href="http://github.com/anutron/mootools-depender/tree/master#readme" target="readme">the readme on github</a>.</p>
	</div>
</div>
<div id="warn_url">
	You must select at least one dependency.
</div>
<div id="copier">
	<h2>Copy
		<a id="close_copier" class="button">close</a>
		</h2>
	<p>Copy the selected text:</p>
	<p><input type="text"/></p>
</div>