<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>Raspberry Pi Wather Monitor</title>
	<link rel="stylesheet" type="text/css" href="style.css">
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
		google.load("visualization", "1", {ldelim}packages:["corechart"] {rdelim});

		{foreach from=$station_data.sensors item=sensor}  <!-- loop through each sensor -->
		{if $sensor.name eq 'dht11' || $sensor.name eq 'dht22'} <!-- detech the sensor -->
		<!-- We need to create a graph function for the two different data values, as tempurature and Humidity wil not always be on the same scale. -->
		function drawChart_{$sensor.name}_humidity() {ldelim}

			var options_{$sensor.name}_humidity = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name}_humidity = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'Humidity'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.humidity} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name}_humidity = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}_humidity'));
			chart_{$sensor.name}_humidity.draw(data_{$sensor.name}_humidity, options_{$sensor.name}_humidity);
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name}_humidity);




		<!-- Now lets do the same for the Temperature data and Timestamp-->
		function drawChart_{$sensor.name}_temp() {ldelim}

			var options_{$sensor.name}_temp = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name}_temp = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'Celsius', 'Fahrenheit'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.c_temp}, {$prow.f_temp} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name}_temp = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}_temp'));
			chart_{$sensor.name}_temp.draw(data_{$sensor.name}_temp, options_{$sensor.name}_temp);
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name}_temp);


		{elseif $sensor.name eq 'bmp085' || $sensor.name eq 'bmp180' || $sensor.name eq 'bmp280'}
		<!-- We need to create graph functions and graphs for pressure and temp because the data values are not even close to the same scales and look like flat lines, and that is boring. -->

		<!-- -->
		<!-- -->
		<!-- Now lets go through each row and only pick out the Pressure and Timestamp -->
		function drawChart_{$sensor.name}_pressure() {ldelim}

			var options_{$sensor.name}_pressure = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name}_pressure = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'Pressure'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.pressure} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name}_pressure = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}_pressure'));
			chart_{$sensor.name}_pressure.draw(data_{$sensor.name}_pressure, options_{$sensor.name}_pressure);
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name}_pressure);




		<!-- -->
		<!-- -->
		<!-- Now lets go through each row and only pick out the Temperature data and Timestamp-->
		function drawChart_{$sensor.name}_temp() {ldelim}

			var options_{$sensor.name}_temp = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name}_temp = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'Celsius', 'Fahrenheit'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.c_temp}, {$prow.f_temp} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name}_temp = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}_temp'));
			chart_{$sensor.name}_temp.draw(data_{$sensor.name}_temp, options_{$sensor.name}_temp);
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name}_temp);





		{elseif $sensor.name eq 'analog_temp_sensor'}
		function drawChart_{$sensor.name}() {ldelim}

			var options_{$sensor.name} = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name} = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'Celsius', 'Fahrenheit'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.c_temp}, {$prow.f_temp} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name} = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}'));
			chart_{$sensor.name}.draw(data_{$sensor.name}, options_{$sensor.name});
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name});





		{elseif $sensor.name eq 'photoresistor'}
		function drawChart_{$sensor.name}() {ldelim}

			var options_{$sensor.name} = {ldelim}
				selectionMode: 'multiple',
				title: "{$sensor.name}",
				crosshair: {ldelim} trigger: 'both' {rdelim},
				chartArea: {ldelim} width: '100%', height: '70%'},
				legend: {ldelim} position: 'none'},
				titlePosition: 'none',
				hAxis: {ldelim} textPosition: 'bottom'{rdelim},
				vAxis: {ldelim} textPosition: 'in'{rdelim},
				explorer:
				{ldelim}
					maxZoomIn: .005,
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'vertical',
					keepInBounds: false
					{rdelim}
				{rdelim};

			var data_{$sensor.name} = google.visualization.arrayToDataTable(
					[
						['Timestamp', 'PhotoLevel'],
						{foreach from=$sensor.data item=prow} <!-- Lets go though all the data and only get the Humidity data and timestamp -->
						['{$prow.timestamp}',  {$prow.photolevel} ],
						{/foreach}
					]
			);
			var chart_{$sensor.name} = new google.visualization.LineChart(document.getElementById('chart_div_{$sensor.name}'));
			chart_{$sensor.name}.draw(data_{$sensor.name}, options_{$sensor.name});
			{rdelim}
		google.setOnLoadCallback(drawChart_{$sensor.name});
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