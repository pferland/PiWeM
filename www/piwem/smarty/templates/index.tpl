<html>
    <head>
        <meta http-equiv="refresh" content="300"> <!-- Refresh every 15 min -->
        <style>
            body
            {
                background-color: #8ab2c0;
            }
            table.main_table
            {
                width : 1850px;
                height: 1000px;
            }
            td.good
            {
                border-style: solid;
                border-width: 1;
                background-color : #00FF00;
            }
            td.bad
            {
                border-style: solid;
                border-width: 1;
                background-color : #FF0000;
            }
            td.warning
            {
                border-style: solid;
                border-width: 1;
                background-color : #FFFF00;
            }
            th
            {
                border-style: solid;
                border-width: 1;
                background-color : lightseagreen;
            }
            td.white
            {
                border-style: solid;
                border-width: 1;
            }
            table.site_table
            {
                border-style: solid;
                border-width: 1;
                width: 200px;
            }
            td.all
            {
                border-style: solid;
                border-width: 1;
            }
            td.center
            {
                text-align: center;
            }
            td.td_align
            {
                vertical-align: center;
                text-align: center;
            }
            a.links
            {
                color: BLACK;
            }
        </style>
    </head>

<body>
<p align="center">
<table>
    <tbody>
{foreach $campus.array as $site}
    {$site.new_row}
        <td class="center">
            <table class='site_table'>
                <tbody>
                <tr>
                    <th class='all'>{$site.name}</a></th>
                </tr>
                <tr>
                    <td class='all'>{$site.date}</td>
                </tr>
                <tr>
                    <td class='{$site.status_color}'>Status: <b>{$site.status|default:'Offline'}</b></td>
                </tr>
                <tr>
                    <td class='all'>Count: <b>{$site.count|default:0}</b> <a class="links" href="graphs.php?id={$site.site_id}&amp;graph=pagecount">Graph</a></td>
                </tr>
                <tr>
                    <td class='{$site.tray1_color}'>Tray 1: <b>{$site.tray_1|default:0}</b> <a class="links" href="graphs.php?id={$site.site_id}&amp;graph=levels&amp;type=tray1">Graph</a></td>
                </tr>
                <tr>
                    <td class='{$site.tray2_color}'>Tray 2: <b>{$site.tray_2|default:0}</b> <a class="links" href="graphs.php?id={$site.site_id}&amp;graph=levels&amp;type=tray2">Graph</a></td>
                </tr>
                </tbody>
            </table>
        </td>
{foreachelse}
        <tr>
            <td>
                There are no sites for this campus yet...
            </td>
        </tr>
{/foreach}
	</tbody>
</table>
</p>
</body>
</html>