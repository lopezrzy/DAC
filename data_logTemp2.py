import minimalmodbus 
from time import sleep
import datetime
import re
import csv
import serial
import io
import os
import sys  # Import sys module for KeyboardInterrupt handling




# Define a function to get the current date and time in the required format
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M:%S")

def parse_data(data):
    # Check if the input contains only 'R', 'H', 'T', 'a', and allowed special characters
    date, time_ = get_datetime()
    humidity = None
    temperature = None 
    # Check if only the characters in [] exist in the string
    if re.match(r'^[RH= Ta.0-9\'C % ]+$', data):
        # Use regular expressions to extract numeric values for RH and Ta
        rh_match = re.search(r'RH= ([\d.]+)', data)
        ta_match = re.search(r'Ta= ([\d.]+)', data)
        # Check if both matches are found
        if rh_match and ta_match:
            humidity = float(rh_match.group(1))
            temperature = float(ta_match.group(1))
                
    return humidity, temperature, date, time_ 

# Configuration of GMP-252 ID=43
carbo_43 = minimalmodbus.Instrument('/dev/ttyACM0',43)
carbo_43.serial.baudrate = 19200
carbo_43.serial.bytesize = 8
carbo_43.serial.parity = minimalmodbus.serial.PARITY_NONE
carbo_43.serial.stopbits = 2
carbo_43.mode = minimalmodbus.MODE_RTU
carbo_43.clear_buffers_before_each_transaction = True
carbo_43.close_port_after_each_call = True

# Configuration of GMP-252 ID=44
carbo_44 = minimalmodbus.Instrument('/dev/ttyACM0',44)
carbo_44.serial.baudrate = 19200
carbo_44.serial.bytesize = 8
carbo_44.serial.parity = minimalmodbus.serial.PARITY_NONE
carbo_44.serial.stopbits = 2
carbo_44.mode = minimalmodbus.MODE_RTU
carbo_44.clear_buffers_before_each_transaction = True
carbo_44.close_port_after_each_call = True
  
# Configuration of HMP-155
serial_THUM = serial.Serial("/dev/ttyACM0",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False,
                   timeout=2)

THUM_00 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))
THUM_01 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))

print(THUM_00)
print(THUM_01)


# Generate a unique filename with a timestamp
timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')

# Define the file path for the CSV file
data_pathway = f"/home/dac/DAC/meas/sensors_readings_{timestamp}.csv"
print (data_pathway)

# Check if the file is empty
file_exists = os.path.exists(data_pathway) and os.path.getsize(data_pathway) > 0

try:
    with open(data_pathway, mode='a', newline='') as csv_file:
        fieldnames = ['Date', 'Time', 'IO', 'Temp', 'Humidity', 'CO2 conc']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header only if the file is empty
        if not file_exists:
          writer.writeheader()
          print('writing header')
          
        while True:
            date, time = get_datetime()
            try:
                carbon_conc_43 = carbo_43.read_float(1, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'IO': "Inlet", 'CO2 conc': carbon_conc_43})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading carbo_43 at {now[1]} on {now[0]}: {e}")

            try:
                carbon_conc_44 = carbo_44.read_float(1, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'IO': "Outlet", 'CO2 conc': carbon_conc_44})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading carbo_44 at {now[1]} on {now[0]}: {e}")

            try:
                THUM_00.write("OPEN 01\r\n")
                THUM_00.flush()
                sleep(1)
                THUM_00.write("SEND\r\n")
                THUM_00.flush()
                sleep(1)
                data_00 = THUM_00.readline().strip()
                rh, temperature, date, time_  = parse_data(data_00)
                writer.writerow({'Date': date, 'Time': time_, 'IO': "Inlet", 'Temp': temperature, 'Humidity': rh})
                csv_file.flush()  # Flush the buffer to ensure data is written immediately
                sleep(5)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_00 at {now[1]} on {now[0]}: {e}")
                
            try:
                THUM_01.write("OPEN 01\r\n")
                THUM_01.flush()
                sleep(1)
                THUM_01.write("SEND\r\n")
                THUM_01.flush()
                sleep(1)
                data_01 = THUM_01.readline().strip()
                rh, temperature, date, time_  = parse_data(data_01)
                writer.writerow({'Date': date, 'Time': time_, 'IO': "Outlet", 'Temp': temperature, 'Humidity': rh})
                csv_file.flush()  # Flush the buffer to ensure data is written immediately
                sleep(5)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_01 at {now[1]} on {now[0]}: {e}")

except KeyboardInterrupt:
    # Close serial ports only if they are open
    if carbo_43.serial.is_open:
        carbo_43.serial.close()
    if carbo_44.serial.is_open:
        carbo_44.serial.close()

    print("Ports Closed")
finally:
    # Close the CSV file before exiting
    if 'csv_file' in locals():
        csv_file.close()
    print("CSV file closed. Program stopped.")
    sys.exit(0)  # Exit the program gracefully
