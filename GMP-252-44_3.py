import minimalmodbus
from time import sleep
import csv
from datetime import datetime
import sys

# Generate a unique filename with a timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
csv_filename = f"sensor_readings_{timestamp}.csv"

carbo_44 = minimalmodbus.Instrument('/dev/ttyACM0', 44, debug=False)
carbo_44.serial.baudrate = 19200
carbo_44.serial.bytesize = 8
carbo_44.serial.parity = minimalmodbus.serial.PARITY_NONE
carbo_44.serial.stopbits = 2
carbo_44.mode = minimalmodbus.MODE_RTU

# Good practice to clean up before and after each execution
carbo_44.clear_buffers_before_each_transaction = True
carbo_44.close_port_after_each_call = True

# Open the CSV file in write mode and create a CSV writer
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ["Timestamp", "CO2 Concentration (ppm)"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    try:
        while True:
            carbon_conc = carbo_44.read_float(1, 3, 2, 0)

            # Get the current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Write the readings to the CSV file
            writer.writerow({"Timestamp": current_time, "CO2 Concentration (ppm)": carbon_conc})
            csv_file.flush()

            sleep(60)  # Sleep for 60 seconds (1 minute)

    except KeyboardInterrupt:
        carbo_44.serial.close()
        print("Ports Now Closed")

# Redirect stdout to /dev/null to suppress console output
sys.stdout = open('/dev/null', 'w')
