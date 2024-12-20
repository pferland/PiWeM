{include file="graphing_head.tpl"}
<table style="width: 100%;">
	<tr>
		<td style=" height:29px">
			<form method="post">
				<select name="station">
					{foreach from=$stations item=station}
						<option value="{$station.station_hash}">{$station.station_name}</option>
					{/foreach}
				</select>
			</form>
		</td>
	</tr>
	<tr>
		<td style="height: 100%">
			<table style="width: 100%">
				<tr>
					<td style="width: 50%; vertical-align:top; text-align:left;">
						<ul>
							<li>
								Station Name: {$station_data.station_name}
							</li>
							<li>
								Last Update: {$station_data.lastupdate}
							</li>
							<li>
								Altitude: {$station_data.altitude} Meters
							</li>
							<li>
								<a href="station_power.php?station_hash={$station_data.station_hash}">Power Usage Charts</a>
							</li>
						</ul>
					</td>

					<td style="width: 50%; text-align:right">
						{if $camera_enabled eq 1}
						<img src="{$camera.image_tn_path}" height="320px">
						{/if}
					</td>
				</tr>
				{foreach from=$station_data.sensors item=sensor}
					<th><br><br><h2>{$sensor.name}</h2></th>
					{if $sensor.name eq 'dht11' || $sensor.name eq 'dht22'} <!-- detect the sensor -->
						<tr>
							<th>Humidity</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}_humidity" style="width: 100%; height: 100%; vertical-align: top"></div>
							</td>
						</tr>
						<tr>
							<th>Temperature</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}_temp" style="width: 100%; height: 100%; vertical-align: top"></div>
								<img height="25" border="0">
							</td>
						</tr>

					{elseif $sensor.name eq 'bmp085' || $sensor.name eq 'bmp180' || $sensor.name eq 'bmp280'}
						<tr>
							<th>Pressure</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}_pressure" style="width: 100%; height: 100%; vertical-align: top"></div>
							</td>
						</tr>
						<tr>
							<th>Temperature</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}_temp" style="width: 100%; height: 100%; vertical-align: top"></div>
								<img height="25" border="0">
							</td>
						</tr>

					{elseif $sensor.name eq 'analog_temp_sensor'}
						<tr>
							<th>Temperature</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}" style="width: 100%; height: 100%; vertical-align: top"></div>
								<img height="25" border="0">
							</td>
						</tr>

					{elseif $sensor.name eq 'photoresistor'}
						<tr>
							<th>PhotoLevel</th>
						</tr>
						<tr>
							<td style="height:300px; vertical-align: top" colspan="2">
								<div id="chart_div_{$sensor.name}" style="width: 100%; height: 100%; vertical-align: top"></div>
								<img height="25" border="0">
							</td>
						</tr>
					{/if}
				{/foreach}
			</table>
		</td>
	</tr>
</table>
{include file="footer.tpl"}