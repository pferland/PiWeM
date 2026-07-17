#!/usr/bin/env python3
import sys
import os
import time
import argparse

# Color mappings
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

# Ensure imports work from the script's directory first
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM


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
            # Use the middle timestamp of the bucket
            downsampled_timestamps.append(bucket_ts[len(bucket_ts) // 2])
            
    return downsampled_values, downsampled_timestamps


def plot_ascii(values, timestamps, title, field_name, unit, height=15, width=60, use_color=True, show_sma=False, sma_window=5):
    """Draw a beautiful colored ASCII/ANSI chart representing sensor values and moving average."""
    if not values:
        print(f"{COLOR_RED}No data available to plot.{COLOR_RESET}")
        return

    # Detect console width to prevent line wrapping
    import shutil
    term_width, _ = shutil.get_terminal_size(fallback=(80, 24))
    max_plot_width = term_width - 12
    if max_plot_width < 10:
        max_plot_width = 10

    actual_width = min(len(values), width, max_plot_width)

    # Downsample values and timestamps if they exceed actual_width to show the entire range
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

    # X-axis timestamps (align with grid index positions)
    if timestamps:
        ts_line = [" "] * len(values)
        indices = [0, len(values) // 2, len(values) - 1]
        indices = sorted(list(set(indices)))
        
        positions = []
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


def plot_combined_ascii(datasets, height=15, use_color=True):
    """Draw a single ASCII chart combining multiple sensor datasets."""
    # datasets is a list of tuples: (values, timestamps, title, field_name, unit)
    datasets = [d for d in datasets if d[0]]
    if not datasets:
        print(f"{COLOR_RED}No data available to plot.{COLOR_RESET}")
        return

    # Find global min and max
    all_values = []
    max_len = 0
    for values, _, _, _, _ in datasets:
        all_values.extend(values)
        if len(values) > max_len:
            max_len = len(values)

    if not all_values:
        print(f"{COLOR_RED}No data values found.{COLOR_RESET}")
        return

    min_val = min(all_values)
    max_val = max(all_values)
    val_range = max_val - min_val
    if val_range == 0:
        val_range = 1.0

    c_axis = COLOR_CYAN if use_color else ""
    c_text = COLOR_YELLOW if use_color else ""
    c_bold = COLOR_BOLD if use_color else ""
    c_reset = COLOR_RESET if use_color else ""

    # Symbols and colors for different series
    symbols = [
        ("•", "\033[92m"),  # Green Dot
        ("x", "\033[93m"),  # Yellow x
        ("*", "\033[96m"),  # Cyan Star
        ("+", "\033[95m"),  # Magenta Plus
        ("o", "\033[91m"),  # Red o
        ("#", "\033[94m"),  # Blue Hash
        ("~", "\033[90m"),  # Grey Wave
    ]

    # Generate grid
    grid_width = max_len
    grid = [[" " for _ in range(grid_width)] for _ in range(height)]

    # Plot each series
    for idx, (values, _, _, _, _) in enumerate(datasets):
        sym_char, sym_color = symbols[idx % len(symbols)]
        c_series = sym_color if use_color else ""
        
        offset = grid_width - len(values)
        for col, val in enumerate(values):
            row = int((val - min_val) / val_range * (height - 1))
            row = max(0, min(height - 1, row))
            grid[height - 1 - row][offset + col] = f"{c_series}{sym_char}{c_reset}"

    # Draw Banner/Header
    border = "=" * (grid_width + 12)
    print(f"{c_axis}{border}{c_reset}")
    title_str = "Combined Sensor Plot"
    print(f" {c_bold}{title_str.center(grid_width + 10)}{c_reset}")
    print(f"{c_axis}{border}{c_reset}")

    # Draw rows with Y-axis labels
    for r in range(height):
        current_y_val = max_val - (r * val_range / (height - 1))
        y_label = f"{c_text}{current_y_val:7.2f}{c_reset} {c_axis}|{c_reset} "
        row_str = "".join(grid[r])
        print(y_label + row_str)

    # Bottom border
    print(" " * 8 + f"{c_axis}+{c_reset}" + f"{c_axis}{'-' * grid_width}{c_reset}")

    # X-axis timestamps (align with grid index positions of the longest series)
    longest_ts = []
    for _, ts, _, _, _ in datasets:
        if len(ts) == max_len:
            longest_ts = ts
            break

    if longest_ts:
        ts_line = [" "] * grid_width
        indices = [0, grid_width // 2, grid_width - 1]
        indices = sorted(list(set(indices)))
        
        for idx in indices:
            ts = str(longest_ts[idx])
            if " " in ts:
                ts = ts.split(" ")[1][:8]  # HH:MM:SS
            elif "T" in ts:
                ts = ts.split("T")[1][:8]
            else:
                ts = ts[:8]
            
            start_pos = idx - len(ts) // 2
            if start_pos < 0:
                start_pos = 0
            if start_pos + len(ts) > grid_width:
                start_pos = grid_width - len(ts)
            
            for i, char in enumerate(ts):
                if 0 <= start_pos + i < grid_width:
                    ts_line[start_pos + i] = char
                    
        ts_str = " " * 9
        for char in ts_line:
            if char != " ":
                ts_str += f"{c_text}{char}{c_reset}"
            else:
                ts_str += " "
        print(ts_str)

    # Print combined legend
    legend_parts = []
    for idx, (values, _, title, field_name, unit) in enumerate(datasets):
        sym_char, sym_color = symbols[idx % len(symbols)]
        c_series = sym_color if use_color else ""
        legend_parts.append(f"{c_series}{sym_char}{c_reset} {title} ({values[-1]:.1f}{unit})")
    
    print(f"\n {c_bold}Legend:{c_reset}  " + "  |  ".join(legend_parts))


def run(settings, sensor_opt, field_opt, limit, hours, height, use_color, show_sma=False, sma_window=5, combine=False):
    """Query data using the PiWeM library database helpers and plot all active sensors."""
    if hours == "all":
        hours = None
    elif limit is None and (hours is None or hours <= 0):
        limit = 50

    try:
        mon = PiWeM.PiWeM(settings=settings)
    except Exception as e:
        print(f"{COLOR_RED}Failed to initialize PiWeM library: {e}{COLOR_RESET}")
        sys.exit(1)

    # Determine which sensors to plot
    active_sensors = []
    
    # Standard field helper mappings
    sensor_fields = {
        "dht11": [("temp", "°C", "DHT11 Temperature"), ("humidity", "%", "DHT11 Humidity")],
        "dht22": [("temp", "°C", "DHT22 Temperature"), ("humidity", "%", "DHT22 Humidity")],
        "am2302": [("temp", "°C", "AM2302 Temperature"), ("humidity", "%", "AM2302 Humidity")],
        "bmp085": [("temp", "°C", "BMP085 Temperature"), ("pressure", "Pa", "BMP085 Pressure")],
        "bmp180": [("temp", "°C", "BMP180 Temperature"), ("pressure", "Pa", "BMP180 Pressure")],
        "bmp280": [("temp", "°C", "BMP280 Temperature"), ("pressure", "Pa", "BMP280 Pressure")],
        "photoresistor": [("photolevel", "Units", "Photoresistor Level")],
        "thermistor": [("temp", "°C", "Thermistor Temperature")],
        "analog_temp_sensor": [("temp", "°C", "Analog Temp Temperature")],
        "wind": [("wind_speed", "m/s", "Wind Speed")],
        "cpu": [("temp", "°C", "CPU Temperature")]
    }

    if sensor_opt in ["auto", "all"]:
        active_sensors = mon.get_registered_sensors()
    else:
        # User defined a specific sensor (e.g. dht22)
        target_sensor = sensor_opt.lower()
        if field_opt in ["auto", "all"]:
            # Get all fields for this sensor
            if target_sensor in sensor_fields:
                for f_name, f_unit, f_title in sensor_fields[target_sensor]:
                    active_sensors.append((target_sensor, f_name, f_unit, f_title))
            else:
                # Fallback to temp if unknown sensor
                active_sensors.append((target_sensor, "temp", "°C", f"{sensor_opt.upper()} Temperature"))
        else:
            # User defined a specific field
            unit = "°C" if field_opt == 'temp' else ("%" if field_opt == 'humidity' else ("Pa" if field_opt == 'pressure' else "Units"))
            active_sensors = [(target_sensor, field_opt, unit, f"{sensor_opt.upper()} {field_opt.capitalize()}")]

    # Plot each detected sensor
    plots_drawn = 0
    if combine:
        datasets = []
        import shutil
        term_width, _ = shutil.get_terminal_size(fallback=(80, 24))
        max_plot_width = term_width - 12
        if max_plot_width < 10:
            max_plot_width = 10

        for sensor, field, unit, title in active_sensors:
            queried_data = mon.get_historical_sensor_data(sensor, field, limit=limit, hours=hours)
            if not queried_data:
                continue

            values = [float(row[0]) for row in queried_data]
            timestamps = [row[1] for row in queried_data]

            actual_width = min(len(values), max_plot_width)
            if len(values) > actual_width:
                values, timestamps = downsample_data(values, timestamps, actual_width)
            
            datasets.append((values, timestamps, title, field, unit))
            plots_drawn += 1

        if datasets:
            plot_combined_ascii(datasets, height=height, use_color=use_color)
            print("\n")
    else:
        for sensor, field, unit, title in active_sensors:
            queried_data = mon.get_historical_sensor_data(sensor, field, limit=limit, hours=hours)

            if not queried_data:
                continue

            plots_drawn += 1
            values = [float(row[0]) for row in queried_data]
            timestamps = [row[1] for row in queried_data]

            plot_ascii(
                values=values,
                timestamps=timestamps,
                title=f"Historical - {title}",
                field_name=field.capitalize(),
                unit=unit,
                height=height,
                width=len(values),
                use_color=use_color,
                show_sma=show_sma,
                sma_window=sma_window
            )
            print("\n")

    if plots_drawn == 0:
        print(f"{COLOR_YELLOW}No historical sensor data found.{COLOR_RESET}")
        print("To verify and resolve this:")
        print("1. Confirm that you have logged data for the selected sensor in the database.")
        print(f"2. Your current station hash is: {COLOR_BOLD}{mon.station_hash}{COLOR_RESET}")
        print("3. Ensure the main monitoring script is running and logging: monitor.py")


def detect_active_sensors(settings):
    """Determine active sensors/fields based on settings.ini."""
    active = []  # List of tuples: (sensor_name, field_name, unit, title)
    
    # Helper function to check if a setting is enabled (1 or True)
    def is_enabled(key):
        try:
            return int(settings.get(key, 0)) == 1
        except (ValueError, TypeError):
            return False

    if is_enabled('dht11_enabled'):
        active.append(('dht11', 'temp', '°C', 'DHT11 Temperature'))
        active.append(('dht11', 'humidity', '%', 'DHT11 Humidity'))
    if is_enabled('dht22_enabled'):
        active.append(('dht22', 'temp', '°C', 'DHT22 Temperature'))
        active.append(('dht22', 'humidity', '%', 'DHT22 Humidity'))
    if is_enabled('am2302_enabled'):
        active.append(('am2302', 'temp', '°C', 'AM2302 Temperature'))
        active.append(('am2302', 'humidity', '%', 'AM2302 Humidity'))
    if is_enabled('bmp085_enabled'):
        active.append(('bmp085', 'temp', '°C', 'BMP085 Temperature'))
        active.append(('bmp085', 'pressure', 'Pa', 'BMP085 Pressure'))
    if is_enabled('bmp180_enabled'):
        active.append(('bmp180', 'temp', '°C', 'BMP180 Temperature'))
        active.append(('bmp180', 'pressure', 'Pa', 'BMP180 Pressure'))
    if is_enabled('bmp280_enabled'):
        active.append(('bmp280', 'temp', '°C', 'BMP280 Temperature'))
        active.append(('bmp280', 'pressure', 'Pa', 'BMP280 Pressure'))
    if is_enabled('thermistor_enabled'):
        active.append(('thermistor', 'temp', '°C', 'Thermistor Temp'))
    if is_enabled('analog_temp_sensor_enabled'):
        active.append(('analog_temp_sensor', 'temp', '°C', 'Analog Temp Sensor'))
    if is_enabled('photoresistor_enabled'):
        active.append(('photoresistor', 'photolevel', 'Units', 'Photoresistor Level'))
    if is_enabled('wind_enabled'):
        active.append(('wind', 'wind_speed', 'm/s', 'Wind Speed'))

    # If no hardware sensors are enabled, default to CPU Temp
    if not active:
        active.append(('cpu', 'temp', '°C', 'CPU Temperature'))

    return active


def list_active_sensors(settings):
    """List configured and registered sensors."""
    try:
        mon = PiWeM.PiWeM(settings=settings)
    except Exception as e:
        print(f"{COLOR_RED}Failed to initialize PiWeM library: {e}{COLOR_RESET}")
        sys.exit(1)

    print(f"\n{COLOR_BOLD}{COLOR_CYAN}=== PiWeM Available Sensors ==={COLOR_RESET}")
    print(f"Current Station Hash: {COLOR_BOLD}{mon.station_hash}{COLOR_RESET}\n")

    # 1. Configured locally in settings.ini
    local_sensors = detect_active_sensors(settings)
    print(f"{COLOR_BOLD}1. Configured in settings.ini (Local Hardware):{COLOR_RESET}")
    if local_sensors:
        grouped = {}
        for sensor, field, unit, title in local_sensors:
            if sensor not in grouped:
                grouped[sensor] = []
            grouped[sensor].append(field)
        
        for sensor, fields in grouped.items():
            print(f"  - {COLOR_GREEN}{sensor:<20}{COLOR_RESET} (fields: {', '.join(fields)})")
    else:
        print("  - No local hardware sensors enabled in settings.ini")

    print("")

    # 2. Registered in Database
    print(f"{COLOR_BOLD}2. Registered in MySQL Database (Station_sensors):{COLOR_RESET}")
    try:
        db_sensors = mon.get_registered_sensors()
        grouped = {}
        for sensor, field, unit, title in db_sensors:
            if sensor not in grouped:
                grouped[sensor] = []
            grouped[sensor].append(field)
        
        for sensor, fields in grouped.items():
            print(f"  - {COLOR_GREEN}{sensor:<20}{COLOR_RESET} (fields: {', '.join(fields)})")
    except Exception as e:
        print(f"  - {COLOR_RED}Failed to query database: {e}{COLOR_RESET}")
    print("")


def main():
    parser = argparse.ArgumentParser(description="PiWeM CLI Sensor Plotting Utility (Database Reader)")
    parser.add_argument("--sensor", "--sensors", type=str, default="auto", dest="sensor",
                        help="The sensor(s) to read and plot (default: auto-detect; 'all' to show everything).")
    parser.add_argument("--field", type=str, default="auto",
                        help="The field/reading to plot (default: auto-detect).")
    parser.add_argument("--limit", type=int, default=None,
                        help="Maximum number of data points to plot.")
    parser.add_argument("--hour", "--hours", type=str, default="2.0", dest="hours",
                        help="Show data from the last N hours (default: 2.0; 'all' to show all recorded history).")
    parser.add_argument("--height", type=int, default=15,
                        help="Height of the plot in lines.")
    parser.add_argument("--list-sensors", action="store_true",
                        help="List all active/registered sensors available for plotting.")
    parser.add_argument("--moving-average", action="store_true",
                        help="Enable plotting of a Simple Moving Average (SMA) line.")
    parser.add_argument("--moving-avg-size", type=int, default=5,
                        help="The window size for the Simple Moving Average (default: 5).")
    parser.add_argument("--loop", action="store_true",
                        help="Continuously loop and redraw the plots.")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="Sleep time interval in seconds between loops (default: 5.0).")
    parser.add_argument("--combine", action="store_true",
                        help="Plot all active sensors in a single combined chart.")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI terminal colors.")

    args = parser.parse_args()

    use_color = not args.no_color

    hours_val = args.hours
    if hours_val.lower() == "all":
        hours_param = "all"
    else:
        try:
            hours_param = float(hours_val)
        except ValueError:
            print(f"{COLOR_RED}Error: --hours must be a number or 'all'.{COLOR_RESET}")
            sys.exit(1)

    # Setup the settings.ini if not existing
    if not os.path.exists("settings.ini") and os.path.exists("settings.ini.sample"):
        import shutil
        shutil.copy("settings.ini.sample", "settings.ini")

    # Load configuration
    PWMConfig = PiWeMConfig()
    try:
        settings = PWMConfig.ConfigMap("settings").get("settings")
    except Exception:
        settings = {}

    if args.list_sensors:
        list_active_sensors(settings)
        sys.exit(0)

    # Adjust default fields based on selected sensor if a single sensor is manually specified
    # Handled dynamically by run()
    pass

    if args.loop:
        print(f"{COLOR_GREEN}Starting plot loop. Press Ctrl+C to exit.{COLOR_RESET}")
        time.sleep(1.5)
        try:
            while True:
                # Clear screen (ANSI escape code)
                print("\033[H\033[J", end="")
                run(
                    settings=settings,
                    sensor_opt=args.sensor,
                    field_opt=args.field,
                    limit=args.limit,
                    hours=hours_param,
                    height=args.height,
                    use_color=use_color,
                    show_sma=args.moving_average,
                    sma_window=args.moving_avg_size,
                    combine=args.combine
                )
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}Plot loop stopped.{COLOR_RESET}")
    else:
        run(
            settings=settings,
            sensor_opt=args.sensor,
            field_opt=args.field,
            limit=args.limit,
            hours=hours_param,
            height=args.height,
            use_color=use_color,
            show_sma=args.moving_average,
            sma_window=args.moving_avg_size,
            combine=args.combine
        )

if __name__ == "__main__":
    main()
