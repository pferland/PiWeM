import sys, os, secrets
from datetime import datetime

import MySQLdb
from PiWeMConfig.PiWeMConfig import PiWeMConfig

PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings")  # Open settings.ini file and read contents
# ---------------------
STATION_NAME = "Raspberry Pi Weather Station"
HASH_FILE = "station_hash.txt"

def load_station_hash():
    """Reads and cleans the hash from the text file."""
    if not os.path.exists(HASH_FILE):
        print(f"Error: The file '{HASH_FILE}' was not found in the current directory.")
        print(f"Please create it at: {os.path.abspath(HASH_FILE)}")
        sys.exit(1)

    with open(HASH_FILE, "r") as f:
        station_hash = f.read().strip()

    if not station_hash:
        print(f"Error: The file '{HASH_FILE}' is empty. Please add your hash to it.")
        sys.exit(1)

    return station_hash


def register_station():
    # Load the hash dynamically from the text file
    station_hash = load_station_hash()
    secure_station_key = secrets.token_hex(16)
    print(f"Loaded station hash from file: {station_hash}")
    current_time = datetime.now()
    try:
        print(f"Connecting to database 'weather_data'...")
        db = MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password'], db='weather_data')
        cursor = db.cursor()

        # Check if hash already exists
        check_query = "SELECT `station_key` FROM `Stations` WHERE `station_hash` = %s"
        cursor.execute(check_query, (station_hash,))
        result = cursor.fetchone()

        if result:
            existing_key = result[0]
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
                       VALUES (%s, %s, %s, %s) \
                       """
        cursor.execute(insert_query, (secure_station_key, station_hash, STATION_NAME, current_time))
        db.commit()

        new_key = cursor.lastrowid
        print("===================================================================\n")
        print(" SUCCESS: Station registered successfully!")
        print("===================================================================\n")
        print(" ACTION REQUIRED:")
        print(" Please open your 'settings.ini' file and configure this exact line:")
        print(f"\n     station_key = \"{secure_station_key}\"\n")
        print("===================================================================\n")

    except MySQLdb.Error as e:
        print(f"\nDatabase Error: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    register_station()
