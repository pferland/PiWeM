{include file="header.tpl"}
	<table>
		<tr>
		{foreach from=$stations item="station"}
			<td style="vertical-align: top">
			<table style="width: 100%;vertical-align: top">
				<tr class="station_header">
					<th style="width: 100%" align="center" colspan="2"> <a href="station.php?station_hash={$station.station_hash}">{$station.station_name}</a></th>
				</tr>
				<tr class="station_header">
					<th style="width: 100%" align="center" colspan="2"> {$station.last_update}</th>
				</tr>
				{foreach from=$station.sensors key="key" item="sensor"}
					{if $key eq 'photoresistor'}
						<tr class="sensor_header">
							<th colspan="2">Photoresistor</th>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Photolevel</td>
							<td style="width: 70px;text-align: center">{$sensor.photolevel}</td>
						</tr>
					{/if}

					{if $key eq 'dht11' or $key eq 'dht22' or $key eq 'am3202'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Celsius</td>
							<td style="width: 70px;text-align: center">{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Fahrenheit</td>
							<td style="width: 70px;text-align: center">{$sensor.f_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Humidity</td>
							<td style="width: 70px;text-align: center">{$sensor.humidity}</td>
						</tr>
					{/if}

					{if $key eq 'bmp085' or $key eq 'bmp180' or $key eq 'bmp280'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Celsius</td>
							<td style="width: 70px;text-align: center">{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Fahrenheit</td>
							<td style="width: 70px;text-align: center">{$sensor.f_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Pressure</td>
							<td style="width: 70px;text-align: center">{$sensor.pressure}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Altitude</td>
							<td style="width: 70px;text-align:center;">{$sensor.altitude}</td>
						</tr>
					{/if}

					{if $key eq 'thermistor' or $key eq 'db18s20' or $key eq 'analog_temp_sensor'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Celsius</td>
							<td style="width: 70px;text-align: center">{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td style="background-color: #7d87ff">Fahrenheit</td>
							<td style="width: 70px;text-align: center">{$sensor.f_temp}</td>
						</tr>
					{/if}
				{/foreach}
			</table>
			</td>
		{/foreach}
		</tr>
	</table>
{include file="footer.tpl"}