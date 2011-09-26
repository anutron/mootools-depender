<%def name="builder(include_mootools=True, include_reset=True)">
	<!-- packager -->

	% if include_reset:
		<link rel="stylesheet" type="text/css" media="screen" href="/depender/static/reset.css" />
	% endif
	<link rel="stylesheet" type="text/css" media="screen" href="/depender/static/packager.css" />
	% if include_mootools:
		<script type="text/javascript" src="/depender/static/mootools-core-1.3.2.js"></script>
	% endif
	<script type="text/javascript" src="/depender/static/packager.js"></script>
	<script type="text/javascript">document.addEvent('domready', Packager.init);</script>
	<form id="packager" action="/depender/build" method="get" style="margin-top: 10px">
	<input type="hidden" name="download" value="true"/>
	<input type="hidden" name="version" value="${version}"/>

		% for p in packages:
			<div id="package-${p}" class="package">

				<table class="vertical">
					<thead>
						<tr class="first">
							<th>Name</th>
							<td>
								${p}
									<div class="buttons">
									<input type="checkbox" name="excludeLibs" class="toggle" value="${p}"/>
									<div class="enabled">
										<input type="button" class="select" value="select package" />
										<input type="button" class="deselect" value="deselect package" />
										<input type="button" class="disable" value="disable package" />
									</div>
									<div class="disabled">
										<input type="button" class="enable" value="enable package" />
									</div>
								</div>
							</td>
						</tr>
					</thead>
					<tbody>
						% for key in ["web", "description", "copyright", "license", "authors"]:
							% if key in dpdr.packages[p].metadata:
								<%
									klass = "middle"
									if key == "authors":
										klass = "last"
								%>
								<tr class="${klass}">
									<th>${key.capitalize()}</th>
									<td>${markdown(dpdr.packages[p].metadata[key])}</td>
								</tr>
							% endif
						% endfor
					</tbody>
				</table>

				<table class="horizontal">
					<tr class="first">
						<th class="first"></th>
						<th class="middle">File</th>
						<th class="middle">Provides</th>
						<th class="last">Description</th>
					</tr>

					% for filedata in sorted(dpdr.packages[p].files, key=lambda file:file.filename):
					<tr class="middle unchecked">
						<td class="first check">
							<div class="checkbox"></div>
							<%
								if filedata.metadata.has_key('name'):
									name = filedata.metadata['name']
								else:
									name = filedata.shortname.split('/')[-1]

								description = "no description"
								if filedata.metadata.has_key('description'):
									description = filedata.metadata['description']
							%>
							<input type="checkbox" name="require" value="${p}/${name}" data-depends="${', '.join(get_depends(p, filedata.filename))}" />
						</td>
						<td class="middle file">${name}</td>
						<td class="middle provides">${', '.join(get_provides(p, filedata.filename))}</td>
						<td class="last description"><p>${description}</p></td>
					</tr>
					% endfor


				</table>

			</div>
		% endfor

		<p class="submit">
			<input type="reset" value="reset" />
			<input type="submit" value="download" />
		</p>

	</form>
</%def>

