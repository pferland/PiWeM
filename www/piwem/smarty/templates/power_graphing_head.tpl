<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Raspberry Pi Wather Monitor</title>
	<link rel="stylesheet" type="text/css" href="style.css">
	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
	<!--<script type="text/javascript" src="https://www.google.com/jsapi"></script>-->
	<script type="text/javascript">
		/*google.load("visualization", "1", {ldelim}packages:["corechart"] {rdelim});*/
		google.charts.load('current', {ldelim}'packages': ['corechart'] {rdelim});

		{foreach from=$station_power key=itemkey item=value}  <!-- loop through each power category -->
		{if $itemkey eq 'voltage'}

			<!-- We need to create a graph function for the two different data values, as temperature and Humidity wil not always be on the same scale. -->
			function drawChart_voltage() {ldelim}

				var options_voltage = {ldelim}
					title: "Voltage",
					hAxis:  {ldelim}
						title: 'Year',
						titleTextStyle:  {ldelim}
							color: '#333'
							{rdelim},
						slantedText: true,
						slantedTextAngle: 90
						{rdelim},
					vAxis:  {ldelim}
						minValue: 0
						{rdelim},
					explorer:  {ldelim}
						axis: 'horizontal',
						keepInBounds: true,
						maxZoomIn: 0.005
						{rdelim},
					colors: ['#D44E41'],
					{rdelim};

				var data_voltage = google.visualization.arrayToDataTable(
						[
							['Timestamp', 'Voltage'],
							{foreach from=$value item=prow}
							[new Date('{$prow.timestamp}'),  {$prow.voltage} ],
							{/foreach}
						]
				);
				var chart_voltage = new google.visualization.LineChart(document.getElementById('chart_div_voltage'));
				chart_voltage.draw(data_voltage, options_voltage);
			{rdelim}
			google.charts.setOnLoadCallback(drawChart_voltage);

		{elseif $itemkey eq 'current'}
			<!-- We need to create graph functions and graphs for pressure and temp because the data values are not even close to the same scales and look like flat lines, and that is boring. -->

			<!-- -->
			<!-- -->
			<!-- Now lets go through each row and only pick out the Current and Timestamp -->
			function drawChart_current() {ldelim}

				var options_current = {ldelim}
					hAxis:  {ldelim}
						title: 'Year',
						titleTextStyle:  {ldelim}
							color: '#333'
							{rdelim},
						slantedText: true,
						slantedTextAngle: 90
						{rdelim},
					vAxis:  {ldelim}
						minValue: 0
						{rdelim},
					explorer:  {ldelim}
						axis: 'horizontal',
						keepInBounds: true,
						maxZoomIn: 0.005
						{rdelim},
					colors: ['#D44E41'],
					{rdelim};

				var data_current = google.visualization.arrayToDataTable(
						[
							['Timestamp', 'Current mA'],
							{foreach from=$value item=prow}
							[new Date('{$prow.timestamp}'),  {$prow.current_mA} ],
							{/foreach}
						]
				);
				var chart_current = new google.visualization.LineChart(document.getElementById('chart_div_current'));
				chart_current.draw(data_current, options_current);
			{rdelim}
			google.charts.setOnLoadCallback(drawChart_current);


		{elseif $itemkey eq 'power'}
			function drawChart_power() {ldelim}

				var options_power = {ldelim}
					title: "Power (E * I)",
					hAxis:  {ldelim}
						title: 'Year',
						titleTextStyle:  {ldelim}
							color: '#333'
							{rdelim},
						slantedText: true,
						slantedTextAngle: 90
						{rdelim},
					vAxis:  {ldelim}
						minValue: 0
						{rdelim},
					explorer:  {ldelim}
						axis: 'horizontal',
						keepInBounds: true,
						maxZoomIn: 0.005
						{rdelim},
					colors: ['#D44E41'],
					{rdelim};

				var data_power = google.visualization.arrayToDataTable(
						[
							['Timestamp', 'Power mW'],
							{foreach from=$value item=prow}
							[new Date('{$prow.timestamp}'),  {$prow.power_mW} ],
							{/foreach}
						]
				);
				var chart_power = new google.visualization.LineChart(document.getElementById('chart_div_power'));
				chart_power.draw(data_power, options_power);
			{rdelim}
			google.charts.setOnLoadCallback(drawChart_power);
		{/if}
		{/foreach}
	</script>
</head>
<body>
<table style="width: 100%">
	<tr>
		<td colspan="2" align="left" class="sub_header">
			{include file="sub_header.tpl"}
		</td>
	</tr>
	<tr>
		<td width="10%" valign="top" class="contents"><!-- Contents Index -->
			{include file="contents.tpl"}
		</td>
		<td align="center" class="body"><!-- Body of page -->