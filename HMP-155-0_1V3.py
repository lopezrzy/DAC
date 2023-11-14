import serial
import io
import csv
from time import sleep
import time
import re
import datetime

def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M")

def open_device(serial_wrapper, device_number):
    # Open the device
    serial_wrapper.write(f"OPEN {device_number}\r\n")
    serial_wrapper.flush()
    print(f"Device {device_number} is opened")
    sleep(2)

def parse_data(data):
    # Check if the input contains only 'R', 'H', 'T', 'a', and allowed special characters
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    humidity = None
    temperature = None 
    if re.match(r'^[RH= Ta.0-9\'C % ]+$', data):
        # Count the occurrences of "Ta="
        ta_count = data.count("Ta=")
        # Check if "Ta=" appears exactly once
        if ta_count == 1:
            # Use regular expressions to extract numeric values for RH and Ta
            rh_match = re.search(r'RH= ([\d.]+)', data)
            ta_match = re.search(r'Ta= ([\d.]+)', data)
            # Check if both matches are found
            if rh_match and ta_match:
                humidity = float(rh_match.group(1))
                temperature = float(ta_match.group(1))
                
    return humidity, temperature, current_time 
        
        
def read_device(serial_wrapper, device_number,csv_writer):
    # Send the data request
    serial_wrapper.write("SEND\r\n")
    serial_wrapper.flush()
    sleep(5)
    # Read and print the data
    data = serial_wrapper.readline().strip()
    print(f"Data from Device {device_number}: {data}")
        
    humidity, temperature, current_time= parse_data(data)
    # Write data to the CSV file
    csv_writer.writerow([current_time, temperature, humidity, device_number])
    sleep(8)

# Define device numbers for only two devices (0 and 1)
device_numbers = ["0", "1"]

# Serial configuration for the two devices
serial_devices = [serial.Serial("/dev/ttyACM0",
                                baudrate=4800,
                                bytesize=serial.SEVENBITS,
                                parity=serial.PARITY_EVEN,
                                stopbits=serial.STOPBITS_ONE,
                                xonxoff=False,
                                timeout=2) for _ in range(len(device_numbers))]

# TextIOWrapper objects for the two devices
THUM_devices = [io.TextIOWrapper(io.BufferedRWPair(serial_device, serial_device)) for serial_device in serial_devices]

# Generate a unique filename with a timestamp
timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
csv_filename = f"Temperature_RH_{timestamp}.csv"

# Create and open a CSV file for data storage
with open(csv_filename, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write headers to the CSV file
    csv_writer.writerow(["Time", "Temperature (C)", "RH (%)", "Sensor Number"])

    for i, device_number in enumerate(device_numbers):
        open_device(THUM_devices[i], device_number)
    
    try:
        while True:
            for i, device_number in enumerate(device_numbers):
                read_device(THUM_devices[i], device_number, csv_writer)
    
    except KeyboardInterrupt:
        # Clean up when interrupted
        print("Ports Now Closed")
    finally:
        # Close all open ports
        for serial_device in serial_devices:
            serial_device.close()
