#!/bin/bash
cd /opt/RasPiMonitor/
/usr/bin/python monitor.py 1>&2 >> /home/pi/piwem_monitor.log
