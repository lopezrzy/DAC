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

# Define a function to get the current date and time in the required format

def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M")

try:
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['Date',
                       'Time',
                       'Ambient temperature',
                       'Relative humidity',
                       'C_CO2']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            date, time = get_datetime()

            try:
                # Read data from CO2Sensor_44
                carbon_conc = carbo_44.read_float(1, 3, 2, 0)
                sleep(30)
                writer.writerow({'Date': date, 'Time': time, 'C_CO2': carbon_conc})

            except Exception as e:
                now = get_datetime()
                print(f"Error reading CO2Sensor_44 at {now[1]} on {now[0]}: {e}")

    except KeyboardInterrupt:
        carbo_44.serial.close()
        print("Ports Now Closed")
