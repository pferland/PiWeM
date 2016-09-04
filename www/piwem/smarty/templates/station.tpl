<table style="width: 100%;">
	<tr>
		<td style=" height:50px">
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
			<iframe src="station_sensors.php?station_hash={$station_hash}"></iframe>
		</td>
	</tr>
</table>