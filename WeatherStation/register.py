import sys
import os
import secrets
import uuid
import argparse
from datetime import datetime

import MySQLdb
from PiWeMConfig.PiWeMConfig import PiWeMConfig

PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings")  # Open settings.ini file and read contents


def update_settings_ini(station_hash, station_key):
    settings_path = "settings.ini"
    if not os.path.exists(settings_path):
        if os.path.exists("settings.ini.sample"):
            import shutil
            shutil.copy("settings.ini.sample", settings_path)
            print("Created settings.ini from sample.")
        else:
            print("Error: settings.ini not found.")
            return

    with open(settings_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    hash_written = False
    key_written = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("station_hash"):
            new_lines.append(f"station_hash = {station_hash}\n")
            hash_written = True
        elif stripped.startswith("station_key"):
            if not hash_written:
                new_lines.append(f"station_hash = {station_hash}\n")
                hash_written = True
            new_lines.append(f"station_key = {station_key}\n")
            key_written = True
        else:
            new_lines.append(line)

    if not hash_written:
        new_lines.append(f"station_hash = {station_hash}\n")
    if not key_written:
        new_lines.append(f"station_key = {station_key}\n")

    with open(settings_path, "w") as f:
        f.writelines(new_lines)
    print("settings.ini updated successfully.")


def get_or_generate_station_hash():
    # 1. Try to load from settings
    station_hash = settings.get('station_hash', '').strip().replace("'", "").replace('"', '')
    
    # 2. Fallback to station_hash.txt if settings is empty or a placeholder
    if not station_hash or "REPLACE" in station_hash:
        if os.path.exists("station_hash.txt"):
            with open("station_hash.txt", "r") as f:
                station_hash = f.read().strip()
                print(f"Loaded legacy station hash from station_hash.txt: {station_hash}")

    # 3. Generate new UUID if still empty
    if not station_hash or "REPLACE" in station_hash:
        station_hash = str(uuid.uuid4())
        print(f"Generated new station hash: {station_hash}")

    return station_hash


def get_or_generate_station_key():
    station_key = settings.get('station_key', '').strip().replace("'", "").replace('"', '')
    if not station_key or "REPLACE" in station_key:
        station_key = secrets.token_hex(16)
        print("Generated new secure key.")
    return station_key


def register_station(station_name):
    station_hash = get_or_generate_station_hash()
    station_key = get_or_generate_station_key()

    try:
        print(f"Connecting to database 'weather_data'...")
        db = MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password'],
                             db='weather_data')
        cursor = db.cursor()

        # Check if hash already exists
        check_query = "SELECT `station_key` FROM `Stations` WHERE `station_hash` = %s"
        cursor.execute(check_query, (station_hash,))
        result = cursor.fetchone()

        if result:
            print("===================================================================\n")
            print(" WARNING: This station is already registered in the database!")
            print(" Registration skipped to prevent duplicate entries.")
            print("===================================================================\n")
            update_settings_ini(station_hash, station_key)
            return

        # Insert new station
        print(f"Registering station with generated secure key...")
        current_time = datetime.now()

        insert_query = """
                       INSERT INTO `Stations` (`station_key`, `station_hash`, `station_name`, `timestamp`)
                       VALUES (%s, %s, %s, %s)
                       """
        cursor.execute(insert_query, (station_key, station_hash, station_name, current_time))
        db.commit()

        # Automatically update settings.ini in place
        update_settings_ini(station_hash, station_key)

        print("===================================================================\n")
        print(" SUCCESS: Station registered successfully!")
        print("===================================================================\n")
        print(" ACTION REQUIRED:")
        print(" Your settings.ini file has been automatically updated with:")
        print(f"     station_hash = {station_hash}")
        print(f"     station_key = {station_key}")
        print("===================================================================\n")

    except MySQLdb.Error as e:
        print(f"\nDatabase Error: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register a PiWeM Weather Station in the database.")
    parser.add_argument(
        "-n", "--StationName",
        type=str,
        default="Raspberry Pi Weather Station",
        help="Specify a custom name for the weather station."
    )
    args = parser.parse_args()

    register_station(station_name=args.StationName)