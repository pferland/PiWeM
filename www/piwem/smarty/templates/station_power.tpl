{include file="power_graphing_head.tpl"}
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
						</ul>
					</td>
				</tr>
				<th>
					<br>
					<br>
					<h2>Power Usage</h2>
				</th>
				<tr>
					<th>Voltage</th>
				</tr>
				<tr>
					<td style="height:300px; vertical-align: top">
						<div id="chart_div_voltage" style="width: 100%; height: 100%; vertical-align: top"></div>
					</td>
				</tr>
				<tr>
					<th>Current</th>
				</tr>
				<tr>
					<td style="height:300px; vertical-align: top">
						<div id="chart_div_current" style="width: 100%; height: 100%; vertical-align: top"></div>
					</td>
				</tr>
				<tr>
					<th>Power (E * I)</th>
				</tr>
				<tr>
					<td style="height:300px; vertical-align: top">
						<div id="chart_div_power" style="width: 100%; height: 100%; vertical-align: top"></div>
					</td>
				</tr>
			</table>
		</td>
	</tr>
</table>
{include file="footer.tpl"}
