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
# ---------------------
HASH_FILE = "station_hash.txt"


def generate_station_hash():
    station_hash_file = open('station_hash.txt', 'w+')
    station_hash = str(uuid.uuid4())
    station_hash_file.write(station_hash)
    station_hash_file.close()
    return station_hash


def load_station_hash(station_hash_file_path):
    """Reads and cleans the hash from the text file."""
    station_hash = ""
    if not os.path.exists(station_hash_file_path):
        station_hash = generate_station_hash()
    else:
        with open(station_hash_file_path, "r") as f:
            station_hash = f.read().strip()
            print(f"Loaded station hash from file: {station_hash}")
    if not station_hash:
        print(f"Error: Failed to get Station Hash from file or even generate one...")
        sys.exit(1)
    return station_hash


def load_station_key():
    """Reads and cleans the hash from the text file."""
    if not settings['station_key']:
        print("There is no currently set Station Key. We will need to generate one.")
        station_key = secrets.token_hex(16)
    else:
        station_key = settings['station_key']
    return station_key


def register_station(station_name, station_hash_file_path):
    # Load the hash dynamically from the text file
    station_hash = load_station_hash(station_hash_file_path)
    station_key = load_station_key()

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

        print("===================================================================\n")
        print(" SUCCESS: Station registered successfully!")
        print("===================================================================\n")
        print(" ACTION REQUIRED:")
        print(" Please open your 'settings.ini' file and configure this exact line:")
        print(f"\n     station_key = \"{station_key}\"\n")
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

    register_station(station_name=args.name, station_hash_file_path=HASH_FILE)