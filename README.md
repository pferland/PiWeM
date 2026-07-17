# PiWeM: Raspberry Pi Weather Monitor

PiWeM is a highly configurable, modern system of PHP frontend services, database APIs, Python weather station daemons, and desktop clients to gather, log, transmit, and visualize telemetry from local weather sensors.

**Project Phase:** Beta  
**Project Version:** v2.1  
**License:** GNU General Public License v2  

---

## Key Features & Modernizations (v2.1)

### 1. Modernized Template Engine (Twig)
* Fully migrated the Central Server frontend from Smarty to the modern **Twig** template engine.
* Standardized layouts under `.twig` markup, eliminating the legacy `smarty/` folder and `.tpl` dependencies.

### 2. Interactive Theme System
* Built a custom theme override engine supporting directory overrides under `/templates/themes/{theme_name}/`.
* Custom themes only need to override specific templates (like `header.twig` or `graphing_head.twig` for styling); Twig automatically falls back to `/templates/default/` for all other templates.
* Comes with two premium pre-built styles:
  * **Dark**: A clean, modern dark-mode aesthetic.
  * **Space**: A flashy cosmic theme featuring radial background gradients, CSS-animated scrolling starfields, nebulae glows, and custom Google Fonts (*Orbitron* and *Space Grotesk*).
* **Robust State Persistence**: Persists selected themes across page navigation via GET/POST query parameters, persistent cookies, and standard PHP Sessions (`$_SESSION`) for strict browser/subdirectory isolation.

### 3. Dynamic Database Schema & Fallback
* Consolidated weather data queries to fetch from individual sensor tables (`bmp280`, `dht22`, `photoresistor`, etc.) instead of a monolithic single table.
* Implemented automatic fallback probing in `GetStationSensors()` that checks the individual tables if the metadata lookup table is empty.
* Isolated the Central Server UI to only display physical weather stations, filtering out desktop client registrations.
* Removed obsolete power-grid layout visual cards and endpoints.

### 4. Advanced Time-Series Engine
* Swapped out row-based limits for dynamic time-series history filters (e.g. `30 MINUTE`, `12 HOUR`, `24 HOUR`, `7 DAY`, `30 DAY`, `all`).
* Compares UTC database timestamps directly against `UTC_TIMESTAMP()` to avoid timezone mismatches.
* Automatically normalizes plural/singular user input (e.g., `24 HOURS` $\rightarrow$ `24 HOUR`) to comply with SQL `INTERVAL` syntax rules.
* **$O(N)$ Telemetry Merging**: Optimized the API data merger to aggregate rows in an $O(N \log N)$ sorting and $O(N)$ linear pass. Grouping timestamps within a 5-second window resolves sub-second sensor reading offsets, reducing response times for large datasets (5,000+ rows) from 10+ seconds to **under 0.8 seconds**.

### 5. Desktop GUI Client
* A fully functional GUI client (`client.py`) supporting PyQt6, PyQt5, and PySide2 fallbacks.
* Features a premium dark mode stylesheet, active station lists, automatic refresh toggles, and real-time telemetry panels.
* **QPainter Vector Plotting**: Supports rendering historical line charts (with 5-Point Simple Moving Average dashed lines and minimum, maximum, current, and average statistics) dynamically via built-in `QPainter` graphics.

### 6. Interactive CLI Client & Plotter
* Added an interactive command-line client (`cli_client.py`) utilizing Python's standard `cmd` module.
* Runs in any standard terminal shell with **zero external dependencies**.
* **Integrated ASCII Plotting**: Plots high-resolution charts in the terminal (with 5-Point Simple Moving Average curves `~` and statistics) for fields like temperature, humidity, pressure, and wind speed.
* Safe string formatting handling prevents crashes from database `NULL` values.
* **Live Shell Watch**: Added the `live` (alias `watch`) command, enabling a full-screen, 10-second auto-refresh terminal monitoring panel.

---

## Requirements

### Hardware (Weather Station Node)
* Raspberry Pi (any version)
* One or more of the following sensors:
  * DHT11, DHT22, AM2302
  * BMP085, BMP180, BMP280
  * PCF8591 (8-bit 4-channel A/D converter for photoresistors, analog thermistors, etc.)
  * Anemometer / Wind direction sensors

### Central Server (WWW & API)
* PHP 8.0 or later
* PHP Extensions: `pdo`, `pdo_mysql`, `session`
* Twig template engine (loaded from `/usr/share/php/Twig/autoload.php` via standard package configuration)
* MariaDB / MySQL Server
* Apache / Nginx Web Server

### Desktop Clients
* Python 3
* *For GUI Client:* PyQt6
* *For CLI Client:* Standard Python library only (no external packages required)

---

## Directory Structure

* **`/CentralServer/piwem/`**
  * Core PHP viewer pages (`index.php`, `station.php`, `graphs.php`).
  * `lib/`: Includes DB logic (`SQL.php`), Central API (`PiWeMAPI.inc.php`), and Frontend controller (`PiWeMFront.inc.php`).
  * `templates/default/`: The baseline default Twig template layouts.
  * `templates/themes/`: Contains customized visual styles (e.g. `dark`, `space`).
  * `Scripts/`: Command-line server tools (like `register.php` node registering script).
* **`/WeatherStation/`**
  * `monitor.py`: Daemon/cron script to read local sensors and upload data.
  * `settings.ini`: Settings file configuring active pins, sensors, and Central Server details.
  * `register.py`: CLI script to request credentials from the Central Server.
* **`/DesktopClient/`**
  * `client.py`: The PyQt GUI client.
  * `cli_client.py`: The new interactive terminal client.
  * `settings.ini`: Connection credentials pointing to the Central Server.

---

## Installation & Setup

### 1. Database Setup
Import the baseline database structure to your MariaDB/MySQL instance:
```bash
mysql -u root -p < blank.sql
```

### 2. Central Server Deployment
1. Copy the contents of `/CentralServer/piwem/` to your web server root (e.g., `/var/www/html/piwem/`).
2. Create your site configuration by copying the sample:
   ```bash
   cp lib/config.php.sample lib/config.php
   ```
3. Edit `lib/config.php` and fill in your database credentials and default settings.

### 3. Weather Station Registration
Register your station node to get an API credential hash:
```bash
python3 register.py --StationName="ThinkPad-X1-Station" --ServerURL="http://192.168.1.155/piwem"
```
This automatically updates your local `settings.ini` with the credentials.

### 4. Running the Monitor
Run the monitor script on the Raspberry Pi:
```bash
python3 monitor.py --Verbose
```
*Tip: Set up a crontab entry to run `run.sh` periodically (e.g., every hour).*

---

## Usage: Interactive CLI Client

Launch the interactive telemetry shell from the `DesktopClient` folder:
```bash
./cli_client.py
```

### Interactive Command List:
* **`list`** (or **`ls`**): Fetches and prints all registered stations, their last update timestamps, and unique hashes.
* **`select <ID_or_Hash>`** (or **`sel`**): Selects a station to monitor.
* **`telemetry`** (or **`tel`**): Displays the latest real-time sensor readings.
* **`plot <field> [interval]`** (or **`graph`**): Plots a high-resolution terminal ASCII line chart.
  * *Fields:* `c_temp`, `f_temp`, `humidity`, `pressure`, `altitude`, `photolevel`, `wind_mps`
  * *Intervals:* `12 HOURS`, `24 HOURS`, `7 DAYS`, or limit numbers (default: `24 HOUR`).
  * *Example:* `plot pressure 24 HOURS`
* **`live`** (or **`watch`**): Enters full-screen monitoring mode, automatically clearing the screen and updating telemetry every 10 seconds. Exit with `Ctrl+C`.
* **`settings`**: View or update server URLs and credentials.
* **`exit`** (or **`quit`**): Exits the shell.

---

## Support
Create a ticket on the GitHub issues tracker at: https://github.com/pferland/PiWeM/issues

**The RanInt Dev Team**  
- *PFerland*
