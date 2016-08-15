<?php
/*
index.php
Copyright (C) 2013 Phil Ferland

This program is free software; you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

ou should have received a copy of the GNU General Public License along with this program;
if not, write to the

   Free Software Foundation, Inc.,
   59 Temple Place, Suite 330,
   Boston, MA 02111-1307 USA
*/

require "lib/config.php"; #www config
#$config = parse_ini_file($WWWconfig['daemon_path']."/config/config.ini");
require "lib/SQL.php"; #the uh.. SQL class...
require $WWWconfig['http']['smarty_path']."/Smarty.class.php"; #get smarty..

#now lets build the SQL class.
$SQL = new SQL($WWWconfig['SQL']);

#setup smarty
$smarty = new smarty();
$smarty->setTemplateDir( $WWWconfig['http']['smarty_path']."/templates/" );
$smarty->setCompileDir( $WWWconfig['http']['smarty_path']."/templates_c/" );
$smarty->setCacheDir( $WWWconfig['http']['smarty_path']."/cache/" );
$smarty->setConfigDir( $WWWconfig['http']['smarty_path']."/configs/" );






$smarty->display("index.tpl");