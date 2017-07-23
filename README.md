Random Intervals -> PiWeM -> Read-me
=====================================

  A set of highly configurable PHP & Python scripts to gather weather data and log it.

  Project Phase: Alpha
  --------------

    This program is free software; you can redistribute it and/or modify it under
	the terms of the GNU General Public License version 2, as published by the 
	Free Software Foundation.   This program is distributed in the hope that it 
	will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
	of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General 
	Public License for more details. You should have received a copy of the GNU 
	General Public License along with this program; if not, you can get it at: 
		
		Free Software Foundation, Inc.,
		51 Franklin St, Fifth Floor
		Boston, MA  02110-1301 USA
		
	Or go here:  http://www.gnu.org/licenses/gpl-2.0.txt
		
  Requirements:
	Hardware:
		Raspberry Pi (any version)
		    One or more of the following:
			PiCamera
			DHT11, DHT22, AM2302*
			BMP085, BMP180**, BMP280
			PCF8591***
			Photoresistor analog module
			Thermistor analog module

	* = As soon as I figure out the am2302 library it will be supported.
	** = In theory it works, don't have the hardware yet though, so it is untested.
	*** = 8bit 4 channel analog to digital converter. Used for the photo-resistor, analog thermisitor, and maybe some other things in the future

	WWW:
		PHP 5.3 or later
			PDO & PDO-MySQL
			Smarty (If not using the one that PiWeM comes with)
		MariaDB 5.2 or later
		Apache 2.2 or later
		A Web-browser (doh!)

	Daemon:
		Python 2
			MySQLdb
			RPi.GPIO
			json
			math
			uuid
			urllib
			PIL
			Picamera
			Adafruit_BMP.BMP085
			dht11
			PCF8591
			bmp280
		MariaDB or MySQL 5.6+
		
  Summary:
	/PiWeM/www
		/piwem
		The Public Web Viewer for the PiWeM collected data. Can either be used on the Raspberry Pi
		to view the data, or on a central server to have several PiWeM nodes upload their data to.
		
		/Scripts
		If you do use the central server model, you will need to run the scripts in this folder to
		register the PiWeM Nodes to the central server. This is so that the nodes can have an API Key
		generated and their Station Hash stored to associate with it. You will also need to
		set an environment variable $PiWeM_Home to the path of your PiWeM install.
		
	/PiWeM/daemon
		settings.ini
		Holds all the settings for the PiWeM Daemon. What sensors are enabled, what to log and when, 
		do you want a picture taken? Read the settings.ini file fore more information on each of the 
		values.
		
		monitor.py
		The main script of PiWeM. If no arguments are set then it will only run once. If you pass 
		-d then it will run in a daemonized mode and run one loop every time period set in the 
		settings.ini time_sleep value.
		
		run.sh
		This bash script is what I had to use to get the script to run as a crontab job. That was the
		most stable that the script would run as. Running it with the -d argument can run into issues
		over a long period of time. It is preferred to run it as a crontab job. You will also need to
		set an environment variable $PiWeM_Home to the path of your PiWeM install.
		Recommended crontab line is once ever hour:
		0 * * * *    root    /opt/PiWeM/run.sh
		
  Installation:
		Copy /PiWeM/www/piwem/ to your HTTP servers public folder.
		Run the SQL file blank.sql against your MySQL Server.
		Edit the settings.ini file to your liking.
		If you are running the WebViewer as a centralized server for many PiWeM Nodes, then you will 
		need to setup the /www/Scripts/ folder also. It is not recomended to have that folder on the 
		http server, but to run it from the command line.
		Example command for the RegisterNode.php script is:

piwem@PiWeMCentral:/wifidb/piwem/Scripts$ php RegisterNode.php --station_name="Sample Station Name" --station_hash="8b4a1d97-8cb8-4fb6-8c7e-ebb8d2341557"
Station Sample Station Name has the following key assigned to it: MC43MzIzNDQwMCAxNDgwMzAwMjc1MjA5MDEzMjI0Ng==
Done!

  Support:
		Go to the Random Intervals section of these forums http://forum.techidiots.net/forum/
		
    Enjoy!
        The RanInt Dev team
		-PFerland