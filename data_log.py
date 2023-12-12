import minimalmodbus 
from time import sleep
import datetime
import csv
import serial
import io
import os

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
serial_THUM = serial.Serial("/dev/ttyACM1",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False,
                   timeout=2)

THUM_00 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))
THUM_01 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))



# Define a function to get the current date and time in the required format
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M")

# Generate a unique filename with a timestamp
timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')

# Define the file path for the CSV file
data_pathway = f"/home/DAC/meas/sensors_readings_{timestamp}.csv"

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
                    writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "2", 'Temp': temp_value_01, 'Humidity': rh_value_01})
                sleep(1)
                THUM_01.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_01 at {now[1]} on {now[0]}: {e}")

except KeyboardInterrupt:
    # Close serial ports only if they are open
    if carbo_43.serial.is_open:
        carbo_43.serial.close()
    if carbo_43.serial.is_open:
        carbo_43.serial.close()

    print("Ports Closed")
