#!/usr/bin/env python3
import sys
import os
import configparser
from unittest.mock import MagicMock

def setup_mocks():
    # Mock RPi, smbus, and Adafruit_GPIO for non-Raspberry Pi environments
    mock_rpi = MagicMock()
    mock_gpio = MagicMock()
    mock_rpi.GPIO = mock_gpio
    sys.modules['RPi'] = mock_rpi
    sys.modules['RPi.GPIO'] = mock_gpio

    mock_smbus = MagicMock()
    sys.modules['smbus'] = mock_smbus

    mock_adafruit_gpio = MagicMock()
    sys.modules['Adafruit_GPIO'] = mock_adafruit_gpio
    sys.modules['Adafruit_GPIO.I2C'] = MagicMock()

def generate_simulation_configs():
    # Load settings.ini.sample, override local db/uploads, and write settings.ini
    config = configparser.ConfigParser()
    config.read("settings.ini.sample")

    # Override settings to ensure no local DB or internet calls are made
    config.set("settings", "localstorage", "0")
    config.set("settings", "bufferlocally", "0")
    config.set("settings", "upload_to_central_server", "0")
    config.set("settings", "upload_to_weather_underground", "0")

    with open("settings.ini", "w") as f:
        config.write(f)

    with open("station_hash.txt", "w") as f:
        f.write("SIMULATION_STATION_HASH_12345")

    print("[Sim] settings.ini and station_hash.txt generated successfully.")

def run_simulation():
    try:
        from PiWeMConfig.PiWeMConfig import PiWeMConfig
        from PiWeM import PiWeM

        PWMConfig = PiWeMConfig()
        settings = PWMConfig.ConfigMap("settings").get("settings")

        mon = PiWeM.PiWeM(settings=settings)
        mon.verbose = 1
        mon.debug = 1

        print("[Sim] PiWeM initialized successfully.")
        print("[Sim] Running simulation of get_data_trigger()...\n")
        
        # Run a single loop iteration
        mon.get_data_trigger()
        
        print("\n[Sim] Simulation iteration completed successfully!")
    finally:
        # Cleanup settings.ini and station_hash.txt
        if os.path.exists("settings.ini"):
            os.remove("settings.ini")
            print("[Sim] settings.ini cleaned up.")
        if os.path.exists("station_hash.txt"):
            os.remove("station_hash.txt")
            print("[Sim] station_hash.txt cleaned up.")

if __name__ == "__main__":
    print("=== Starting PiWeM Simulation ===")
    setup_mocks()
    generate_simulation_configs()
    run_simulation()
    print("=== Simulation Finished ===")
