import minimalmodbus 
from time import sleep
import datetime
import csv
import serial
import io
import os
import sys  # Import sys module for KeyboardInterrupt handling


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

# Define a function to get the current date and time in the required format
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M")

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



        while True:
            date, time = get_datetime()
            print(writing)

            try:
                THUM_00.write("OPEN 0\r\n")
                THUM_00.flush()
                sleep(1)
                THUM_00.write("SEND\r\n")
                THUM_00.flush()
                sleep(1)
                data_00 = THUM_00.readlines()
                last_line_00 = data_00[-1]
                rh_index_00 = last_line_00.find('RH=')
                temp_index_00 = last_line_00.find("Ta=")
                if rh_index_00 != -1 and temp_index_00 != -1:
                    rh_value_00 = float(last_line_00[rh_index_00 + 3:last_line_00.find('%RH')])
                    temp_value_00 = float(last_line_00[temp_index_00 + 3:last_line_00.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'IO': "Inlet", 'Temp': temp_value_00, 'Humidity': rh_value_00})
                print(f"RH from Device 00: {rh_value_00}")  
                print(f"Temp from Device 00: {temp_value_00}")  
                sleep(1)
                THUM_00.write("CLOSE\r\n")
                sleep(1)
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
                data_01 = THUM_01.readlines()
                last_line_01 = data_01[-1]
                rh_index_01 = last_line_01.find('RH=')
                temp_index_01 = last_line_01.find("Ta=")
                if rh_index_01 != -1 and temp_index_01 != -1:
                    rh_value_01 = float(last_line_01[rh_index_01 + 3:last_line_01.find('%RH')])
                    temp_value_01 = float(last_line_01[temp_index_01 + 3:last_line_01.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'IO': "Outlet", 'Temp': temp_value_01, 'Humidity': rh_value_01})
                print(f"RH from Device 00: {rh_value_01}")  
                print(f"Temp from Device 00: {temp_value_01}")  
                sleep(1)
                THUM_01.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_01 at {now[1]} on {now[0]}: {e}")

except KeyboardInterrupt:


    print("Ports Closed")
finally:
    # Close the CSV file before exiting
    if 'csv_file' in locals():
        csv_file.close()
    print("CSV file closed. Program stopped.")
    sys.exit(0)  # Exit the program gracefully
