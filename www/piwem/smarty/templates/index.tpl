{include file="header.tpl"}
	<table>
		<tr>
		{foreach from=$stations item="station"}
			<td align="center">
			<table style="width: 10%">
				<tr class="station_header">
					<th style="width: 100%" align="center" colspan="2"> <a href="station.php?station_hash={$station.station_hash}">{$station.station_name}</a></th>
				</tr>
				{foreach from=$station.sensors key="key" item="sensor"}
					{if $key eq 'photoresistor'}
						<tr class="sensor_header">
							<th colspan="2">Photoresistor</th>
						</tr>
						<tr class="sensor_values">
							<td>Photolevel</td>
							<td>{$sensor.photolevel}</td>
						</tr>
					{/if}

					{if $key eq 'dht11' or $key eq 'dht22' or $key eq 'am3202'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td>Celsius</td>
							<td>{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td>Fahrenheit</td>
							<td>{$sensor.f_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td>Humidity</td>
							<td>{$sensor.humidity}</td>
						</tr>
					{/if}

					{if $key eq 'bmp085' or $key eq 'bmp180' or $key eq 'bmp280'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td>Celsius</td>
							<td>{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td>Fahrenheit</td>
							<td>{$sensor.f_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td>Pressure</td>
							<td>{$sensor.pressure}</td>
						</tr>
						<tr class="sensor_values">
							<td>Altitude</td>
							<td>{$sensor.altitude}</td>
						</tr>
					{/if}

					{if $key eq 'thermistor' or $key eq 'db18s20' or $key eq 'analog_temp_sensor'}
						<tr class="sensor_header">
							<th colspan="2">{$key}</th>
						</tr>
						<tr class="sensor_values">
							<td>Celsius</td>
							<td>{$sensor.c_temp}</td>
						</tr>
						<tr class="sensor_values">
							<td>Fahrenheit</td>
							<td>{$sensor.f_temp}</td>
						</tr>
					{/if}
				{/foreach}
			</table>
			</td>
		{/foreach}
		</tr>
	</table>
{include file="footer.tpl"}