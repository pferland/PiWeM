#!/usr/bin/env python3
import sys
import os
import urllib.parse
import urllib.request
import json
import configparser
import cmd
import shutil

# ANSI Color constants for flashy terminal output
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_PURPLE = "\033[95m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"


def calculate_moving_average(values, window=5):
    """Calculate a simple moving average with the given window size."""
    sma = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        sub_list = values[start : i + 1]
        sma.append(sum(sub_list) / len(sub_list))
    return sma


def format_converted_value(val, unit):
    """Convert and format the value with other common units."""
    if val is None:
        return "--"
    try:
        val = float(val)
    except ValueError:
        return str(val)

    if unit == "°C":
        val_f = val * 1.8 + 32
        return f"{val:.2f}°C ({val_f:.2f}°F)"
    elif unit == "Pa":
        val_hpa = val / 100.0
        val_inhg = val * 0.0002953
        return f"{val:.2f} Pa ({val_hpa:.1f} hPa | {val_inhg:.2f} inHg)"
    elif unit in ["m/s", "mps"]:
        val_mph = val * 2.23694
        val_kph = val * 3.6
        return f"{val:.2f} m/s ({val_mph:.1f} mph | {val_kph:.1f} km/h)"
    else:
        return f"{val:.2f} {unit}"


def downsample_data(values, timestamps, target_width):
    """Downsample values and timestamps to fit exactly target_width columns."""
    if len(values) <= target_width or target_width <= 0:
        return values, timestamps

    bucket_size = len(values) / target_width
    downsampled_values = []
    downsampled_timestamps = []

    for i in range(target_width):
        start_idx = int(i * bucket_size)
        end_idx = int((i + 1) * bucket_size)
        if start_idx == end_idx:
            end_idx = start_idx + 1
        
        bucket_vals = values[start_idx:end_idx]
        bucket_ts = timestamps[start_idx:end_idx]
        
        if bucket_vals:
            downsampled_values.append(sum(bucket_vals) / len(bucket_vals))
            downsampled_timestamps.append(bucket_ts[len(bucket_ts) // 2])
            
    return downsampled_values, downsampled_timestamps


def plot_ascii(values, timestamps, title, field_name, unit, height=14, width=70, use_color=True, show_sma=True, sma_window=5):
    """Draw a beautiful colored ASCII/ANSI chart representing sensor values and moving average."""
    if not values:
        print(f"{COLOR_RED}No data available to plot.{COLOR_RESET}")
        return

    # Detect console width to prevent line wrapping
    term_width, _ = shutil.get_terminal_size(fallback=(80, 24))
    max_plot_width = term_width - 12
    if max_plot_width < 10:
        max_plot_width = 10

    actual_width = min(len(values), width, max_plot_width)

    # Downsample values and timestamps if they exceed actual_width
    if len(values) > actual_width:
        values, timestamps = downsample_data(values, timestamps, actual_width)

    # Calculate moving average if enabled
    sma_vals = None
    if show_sma:
        sma_vals = calculate_moving_average(values, window=sma_window)

    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val
    if val_range == 0:
        val_range = 1.0

    c_axis = COLOR_CYAN if use_color else ""
    c_plot = COLOR_GREEN if use_color else ""
    c_sma = COLOR_YELLOW if use_color else ""
    c_text = COLOR_YELLOW if use_color else ""
    c_bold = COLOR_BOLD if use_color else ""
    c_reset = COLOR_RESET if use_color else ""

    # Generate grid
    grid = [[" " for _ in range(len(values))] for _ in range(height)]
    
    # 1. Plot original points (Green •)
    for col, val in enumerate(values):
        row = int((val - min_val) / val_range * (height - 1))
        row = max(0, min(height - 1, row))
        grid[height - 1 - row][col] = f"{c_plot}•{c_reset}"

    # 2. Plot moving average points (Yellow ~)
    if show_sma and sma_vals:
        for col, val in enumerate(sma_vals):
            row = int((val - min_val) / val_range * (height - 1))
            row = max(0, min(height - 1, row))
            grid[height - 1 - row][col] = f"{c_sma}~{c_reset}"

    # Draw Banner/Header
    border = "=" * (len(values) + 12)
    print(f"{c_axis}{border}{c_reset}")
    title_str = f"{title} - {field_name} ({unit})"
    print(f" {c_bold}{title_str.center(len(values) + 10)}{c_reset}")
    print(f"{c_axis}{border}{c_reset}")

    # Draw rows with Y-axis labels
    for r in range(height):
        current_y_val = max_val - (r * val_range / (height - 1))
        y_label = f"{c_text}{current_y_val:7.2f}{c_reset} {c_axis}|{c_reset} "
        row_str = "".join(grid[r])
        print(y_label + row_str)

    # Bottom border
    print(" " * 8 + f"{c_axis}+{c_reset}" + f"{c_axis}{'-' * len(values)}{c_reset}")

    # X-axis timestamps
    if timestamps:
        ts_line = [" "] * len(values)
        indices = [0, len(values) // 2, len(values) - 1]
        indices = sorted(list(set(indices)))
        
        for idx in indices:
            ts = str(timestamps[idx])
            if " " in ts:
                ts = ts.split(" ")[1][:8]  # HH:MM:SS
            elif "T" in ts:
                ts = ts.split("T")[1][:8]
            else:
                ts = ts[:8]
            
            start_pos = idx - len(ts) // 2
            if start_pos < 0:
                start_pos = 0
            if start_pos + len(ts) > len(values):
                start_pos = len(values) - len(ts)
            
            for i, char in enumerate(ts):
                if 0 <= start_pos + i < len(values):
                    ts_line[start_pos + i] = char
                    
        ts_str = " " * 9
        for char in ts_line:
            if char != " ":
                ts_str += f"{c_text}{char}{c_reset}"
            else:
                ts_str += " "
        print(ts_str)

    # Print summary statistics and legend
    avg_val = sum(values) / len(values)
    cur_val = values[-1]
    if show_sma:
        print(f"\n {c_bold}Legend:{c_reset} {c_plot}• Actual{c_reset}  {c_sma}~ {sma_window}-Point SMA{c_reset}")
    else:
        print("")

    min_str = format_converted_value(min_val, unit)
    max_str = format_converted_value(max_val, unit)
    cur_str = format_converted_value(cur_val, unit)
    avg_str = format_converted_value(avg_val, unit)

    print(f" {c_bold}Stats:{c_reset}")
    print(f"  - Min:     {c_text}{min_str}{c_reset}")
    print(f"  - Max:     {c_text}{max_str}{c_reset}")
    print(f"  - Current: {c_bold}{c_plot}{cur_str}{c_reset}")
    print(f"  - Avg:     {c_text}{avg_str}{c_reset}")


class PiWeMShell(cmd.Cmd):
    intro = (
        f"\n{COLOR_CYAN}{COLOR_BOLD}===================================================={COLOR_RESET}\n"
        f"   {COLOR_GREEN}{COLOR_BOLD}Welcome to the PiWeM Interactive Telemetry Shell!{COLOR_RESET}\n"
        f"   {COLOR_CYAN}Type 'help' or '?' to list available commands.{COLOR_RESET}\n"
        f"{COLOR_CYAN}{COLOR_BOLD}===================================================={COLOR_RESET}\n"
    )
    prompt = f"{COLOR_CYAN}piwem-cli>{COLOR_RESET} "

    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
        self.config = configparser.ConfigParser()
        self.load_settings()
        self.stations = []
        self.selected_station = None

    def load_settings(self):
        if os.path.exists(self.settings_file):
            self.config.read(self.settings_file)
        if "General" not in self.config:
            self.config["General"] = {}
        
        self.server_url = self.config.get("General", "server_url", fallback="http://localhost/piwem")
        self.station_hash = self.config.get("General", "station_hash", fallback="")
        self.station_key = self.config.get("General", "station_key", fallback="")

    def save_settings(self):
        self.config["General"]["server_url"] = self.server_url
        self.config["General"]["station_hash"] = self.station_hash
        self.config["General"]["station_key"] = self.station_key
        with open(self.settings_file, "w") as f:
            self.config.write(f)
        print(f"{COLOR_GREEN}Settings saved successfully.{COLOR_RESET}")

    def make_api_request(self, mode, extra_params=None):
        if not self.server_url:
            raise Exception("Server URL not configured.")
        if not self.station_hash or not self.station_key:
            raise Exception("Client credentials (Hash/Key) missing. Run 'settings' to configure.")

        api_url = f"{self.server_url.rstrip('/')}/api/api.php"
        params = {
            "station_hash": self.station_hash,
            "station_key": self.station_key,
            "mode": mode
        }
        if extra_params:
            params.update(extra_params)

        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(api_url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = response.read().decode('utf-8')
            if "Invalid Station or Key" in res_data:
                raise Exception("Authentication Failed: Invalid Client Hash/Key combination.")
            return json.loads(res_data)

    def do_settings(self, arg):
        """View or configure connections settings.\nUsage: settings [server_url] [client_hash] [client_key]"""
        args = arg.split()
        if len(args) == 3:
            self.server_url, self.station_hash, self.station_key = args
            self.save_settings()
        elif len(args) == 0:
            print(f"{COLOR_BOLD}Current Settings:{COLOR_RESET}")
            print(f"  - Server URL:  {COLOR_YELLOW}{self.server_url}{COLOR_RESET}")
            print(f"  - Client Hash: {COLOR_YELLOW}{self.station_hash}{COLOR_RESET}")
            print(f"  - Client Key:  {COLOR_YELLOW}{self.station_key[:4]}...{self.station_key[-4:] if len(self.station_key) > 8 else ''}{COLOR_RESET}")
        else:
            print(f"{COLOR_RED}Error: Invalid arguments. Run 'help settings' for usage.{COLOR_RESET}")

    def do_list(self, arg):
        """List registered weather stations.\nUsage: list"""
        print(f"{COLOR_CYAN}Fetching registered stations...{COLOR_RESET}")
        try:
            self.stations = self.make_api_request("liststations")
            if not self.stations:
                print("No stations found.")
                return
            
            print(f"\n{COLOR_BOLD}Registered Stations:{COLOR_RESET}")
            print("-" * 106)
            print(f" {'ID':<3} | {'Station Name':<30} | {'Last Update':<24} | {'Station Hash':<36}")
            print("-" * 106)
            for idx, station in enumerate(self.stations):
                name = station.get("station_name")
                if name is None:
                    name = "Unknown"
                update = station.get("lastupdate")
                if update is None:
                    update = "--"
                shash = station.get("station_hash") or "--"
                print(f" {idx + 1:<3} | {name:<30} | {update:<24} | {shash:<36}")
            print("-" * 106)
            print(f"Select a station using: {COLOR_GREEN}select <ID>{COLOR_RESET}\n")
        except Exception as e:
            print(f"{COLOR_RED}Error: {e}{COLOR_RESET}")

    def do_select(self, arg):
        """Select a weather station for telemetry queries.\nUsage: select <ID_or_Hash>"""
        if not arg:
            print(f"{COLOR_RED}Error: Station ID or Hash required.{COLOR_RESET}")
            return

        if not self.stations:
            # Load stations first
            try:
                self.stations = self.make_api_request("liststations")
            except Exception as e:
                print(f"{COLOR_RED}Failed to load stations: {e}{COLOR_RESET}")
                return

        selected = None
        # Try index lookup
        if arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(self.stations):
                selected = self.stations[idx]
        
        # Try hash match
        if not selected:
            for station in self.stations:
                if station.get("station_hash") == arg:
                    selected = station
                    break

        if selected:
            self.selected_station = selected
            self.prompt = f"{COLOR_CYAN}piwem-cli ({COLOR_GREEN}{selected['station_name']}{COLOR_CYAN})>{COLOR_RESET} "
            print(f"{COLOR_GREEN}Selected station: {COLOR_BOLD}{selected['station_name']}{COLOR_RESET}")
        else:
            print(f"{COLOR_RED}Error: Station not found by index or Hash.{COLOR_RESET}")

    def do_telemetry(self, arg):
        """Display the latest real-time telemetry readings for the selected station.\nUsage: telemetry"""
        if not self.selected_station:
            print(f"{COLOR_RED}Error: No station selected. Run 'list' then 'select' first.{COLOR_RESET}")
            return

        try:
            records = self.make_api_request("readdata", {"target_hash": self.selected_station["station_hash"], "limit": 1})
            if not records:
                print(f"{COLOR_YELLOW}No telemetry recorded for this station.{COLOR_RESET}")
                return
            
            record = records[0]
            station_name = self.selected_station.get('station_name') or 'Unknown'
            print(f"\n{COLOR_BOLD}Latest Telemetry: {station_name}{COLOR_RESET}")
            print("=" * 50)
            
            timestamp = record.get('timestamp')
            timestamp_str = str(timestamp) if timestamp is not None else "--"
            print(f" Timestamp:      {COLOR_YELLOW}{timestamp_str}{COLOR_RESET}")
            
            c_temp = record.get('c_temp')
            c_temp_str = format_converted_value(c_temp, '°C') if c_temp is not None else "--"
            print(f" Temperature:    {COLOR_GREEN}{c_temp_str}{COLOR_RESET}")
            
            humidity = record.get('humidity')
            humidity_str = f"{float(humidity):.1f} %" if humidity is not None else "--"
            print(f" Humidity:       {COLOR_GREEN}{humidity_str}{COLOR_RESET}")
            
            pressure = record.get('pressure')
            pressure_str = format_converted_value(pressure, 'Pa') if pressure is not None else "--"
            print(f" Barometer:      {COLOR_GREEN}{pressure_str}{COLOR_RESET}")
            
            altitude = record.get('altitude')
            altitude_str = f"{float(altitude):.1f} meters" if altitude is not None else "--"
            print(f" Altitude:       {COLOR_GREEN}{altitude_str}{COLOR_RESET}")
            
            photolevel = record.get('photolevel')
            photolevel_str = str(photolevel) if photolevel is not None else "--"
            print(f" Photo Level:    {COLOR_GREEN}{photolevel_str}{COLOR_RESET}")
            
            wind_mps = record.get('wind_mps')
            wind_mps_str = format_converted_value(wind_mps, 'm/s') if wind_mps is not None else "--"
            print(f" Wind Speed:     {COLOR_GREEN}{wind_mps_str}{COLOR_RESET}")
            
            wind_dir = record.get("wind_direction")
            wind_dir_str = f"{wind_dir}°" if wind_dir is not None else "--"
            print(f" Wind Direction: {COLOR_GREEN}{wind_dir_str}{COLOR_RESET}")
            print("=" * 50 + "\n")
        except Exception as e:
            print(f"{COLOR_RED}Error: {e}{COLOR_RESET}")

    def do_plot(self, arg):
        """Plot historical chart for a specific sensor field.\nUsage: plot <field> [limit_or_interval]\n\nAvailable Fields:\n  c_temp, f_temp, humidity, pressure, altitude, photolevel, wind_mps"""
        if not self.selected_station:
            print(f"{COLOR_RED}Error: No station selected. Run 'list' then 'select' first.{COLOR_RESET}")
            return

        args = arg.split()
        if len(args) == 0:
            print(f"{COLOR_BOLD}Available Plot Fields:{COLOR_RESET}")
            print("  c_temp, f_temp, humidity, pressure, altitude, photolevel, wind_mps")
            print(f"\nExample: {COLOR_GREEN}plot c_temp 24 HOUR{COLOR_RESET}")
            return

        field = args[0]
        # Parse limit / interval
        limit = "24 HOUR"
        if len(args) > 1:
            limit = " ".join(args[1:])

        # Map field to human readable labels and units
        field_mappings = {
            "c_temp": ("Temperature", "°C"),
            "f_temp": ("Temperature", "°F"),
            "humidity": ("Humidity", "%"),
            "pressure": ("Pressure", "Pa"),
            "altitude": ("Altitude", "m"),
            "photolevel": ("Photo Level", "Photolevel"),
            "wind_mps": ("Wind Speed", "m/s")
        }

        if field not in field_mappings:
            print(f"{COLOR_RED}Error: Invalid field '{field}'. Run 'help plot' for available options.{COLOR_RESET}")
            return

        label, unit = field_mappings[field]

        print(f"{COLOR_CYAN}Fetching historical telemetry (interval: {limit})...{COLOR_RESET}")
        try:
            records = self.make_api_request("readdata", {
                "target_hash": self.selected_station["station_hash"],
                "limit": limit
            })
            if not records:
                print(f"{COLOR_YELLOW}No data points found for this range.{COLOR_RESET}")
                return

            # API returns newest first. Reverse to show chronological order left-to-right
            records.reverse()

            values = []
            timestamps = []
            for r in records:
                val = r.get(field)
                if val is not None:
                    try:
                        values.append(float(val))
                        timestamps.append(r.get("timestamp", ""))
                    except ValueError:
                        pass

            if not values:
                print(f"{COLOR_YELLOW}No valid numeric data found for field '{field}'.{COLOR_RESET}")
                return

            plot_ascii(
                values=values,
                timestamps=timestamps,
                title=self.selected_station["station_name"],
                field_name=label,
                unit=unit
            )

        except Exception as e:
            print(f"{COLOR_RED}Error: {e}{COLOR_RESET}")

    def do_exit(self, arg):
        """Exit the telemetry shell.\nUsage: exit"""
        print(f"\n{COLOR_CYAN}Goodbye!{COLOR_RESET}\n")
        return True

    def do_quit(self, arg):
        """Exit the telemetry shell.\nUsage: quit"""
        return self.do_exit(arg)

    # Aliases
    do_ls = do_list
    do_sel = do_select
    do_tel = do_telemetry
    do_graph = do_plot


if __name__ == '__main__':
    try:
        shell = PiWeMShell()
        shell.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{COLOR_CYAN}Goodbye!{COLOR_RESET}\n")
