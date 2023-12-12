import minimalmodbus 
from time import sleep
import datetime
import csv
import serial
import io
import os

# Configuration of SQ-618 ID=1
PAR_1 = minimalmodbus.Instrument('/dev/ttyACM0',1)
PAR_1.serial.baudrate = 19200
PAR_1.serial.bytesize = 8
PAR_1.serial.parity = minimalmodbus.serial.PARITY_NONE
PAR_1.serial.stopbits = 1
PAR_1.serial.timeout = 0.5
PAR_1.mode = minimalmodbus.MODE_RTU
PAR_1.clear_buffers_before_each_transaction = True
PAR_1.close_port_after_each_call = True

# Configuration of SQ-618 ID=2
PAR_2 = minimalmodbus.Instrument('/dev/ttyACM0',2)
PAR_2.serial.baudrate = 19200
PAR_2.serial.bytesize = 8
PAR_2.serial.parity = minimalmodbus.serial.PARITY_NONE
PAR_2.serial.stopbits = 1
PAR_2.serial.timeout = 0.5
PAR_2.mode = minimalmodbus.MODE_RTU
PAR_2.clear_buffers_before_each_transaction = True
PAR_2.close_port_after_each_call = True

# Configuration of SQ-618 ID=3
PAR_3 = minimalmodbus.Instrument('/dev/ttyACM0',3)
PAR_3.serial.baudrate = 19200
PAR_3.serial.bytesize = 8
PAR_3.serial.parity = minimalmodbus.serial.PARITY_NONE
PAR_3.serial.stopbits = 1
PAR_3.serial.timeout = 0.5
PAR_3.mode = minimalmodbus.MODE_RTU
PAR_3.clear_buffers_before_each_transaction = True
PAR_3.close_port_after_each_call = True

# Configuration of SQ-618 ID=4
PAR_4 = minimalmodbus.Instrument('/dev/ttyACM0',4)
PAR_4.serial.baudrate = 19200
PAR_4.serial.bytesize = 8
PAR_4.serial.parity = minimalmodbus.serial.PARITY_NONE
PAR_4.serial.stopbits = 1
PAR_4.serial.timeout = 0.5
PAR_4.mode = minimalmodbus.MODE_RTU
PAR_4.clear_buffers_before_each_transaction = True
PAR_4.close_port_after_each_call = True

# Configuration of SP-522 ID=11
Solar_11 = minimalmodbus.Instrument('/dev/ttyACM0',11)
Solar_11.serial.baudrate = 19200
Solar_11.serial.bytesize = 8
Solar_11.serial.parity = minimalmodbus.serial.PARITY_NONE
Solar_11.serial.stopbits = 1
Solar_11.serial.timeout = 0.5
Solar_11.mode = minimalmodbus.MODE_RTU
Solar_11.clear_buffers_before_each_transaction = True
Solar_11.close_port_after_each_call = True

# Configuration of SP-522 ID=12
Solar_12 = minimalmodbus.Instrument('/dev/ttyACM0',12)
Solar_12.serial.baudrate = 19200
Solar_12.serial.bytesize = 8
Solar_12.serial.parity = minimalmodbus.serial.PARITY_NONE
Solar_12.serial.stopbits = 1
Solar_12.serial.timeout = 0.5
Solar_12.mode = minimalmodbus.MODE_RTU
Solar_12.clear_buffers_before_each_transaction = True
Solar_12.close_port_after_each_call = True

# Configuration of SP-522 ID=13
Solar_13 = minimalmodbus.Instrument('/dev/ttyACM0',13)
Solar_13.serial.baudrate = 19200
Solar_13.serial.bytesize = 8
Solar_13.serial.parity = minimalmodbus.serial.PARITY_NONE
Solar_13.serial.stopbits = 1
Solar_13.serial.timeout = 0.5
Solar_13.mode = minimalmodbus.MODE_RTU
Solar_13.clear_buffers_before_each_transaction = True
Solar_13.close_port_after_each_call = True

# Configuration of SP-522 ID=14
Solar_14 = minimalmodbus.Instrument('/dev/ttyACM0',14)
Solar_14.serial.baudrate = 19200
Solar_14.serial.bytesize = 8
Solar_14.serial.parity =minimalmodbus.serial.PARITY_NONE
Solar_14.serial.stopbits = 1
Solar_14.serial.timeout = 0.5
Solar_14.mode = minimalmodbus.MODE_RTU
Solar_14.clear_buffers_before_each_transaction = True
Solar_14.close_port_after_each_call = True

# Configuration of GMP-252 ID=41
carbo_41 = minimalmodbus.Instrument('/dev/ttyACM0',41)
carbo_41.serial.baudrate = 19200
carbo_41.serial.bytesize = 8
carbo_41.serial.parity = minimalmodbus.serial.PARITY_NONE
carbo_41.serial.stopbits = 2
carbo_41.mode = minimalmodbus.MODE_RTU
carbo_41.clear_buffers_before_each_transaction = True
carbo_41.close_port_after_each_call = True

# Configuration of GMP-252 ID=42
carbo_42 = minimalmodbus.Instrument('/dev/ttyACM0',42)
carbo_42.serial.baudrate = 19200
carbo_42.serial.bytesize = 8
carbo_42.serial.parity = minimalmodbus.serial.PARITY_NONE
carbo_42.serial.stopbits = 2
carbo_42.mode = minimalmodbus.MODE_RTU
carbo_42.clear_buffers_before_each_transaction = True
carbo_42.close_port_after_each_call = True

# Configuration of HMP-155
serial_THUM = serial.Serial("/dev/ttyACM1",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False,
                   timeout=2)

THUM_31 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))
THUM_32 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))
THUM_33 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))
THUM_34 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM, serial_THUM))


# Define a function to get the current date and time in the required format
def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y"), now.strftime("%H:%M")

# Define the file path for the CSV file
Climatic_data_pathway = "/home/cdacea/GH_data/climatic_data.csv"

# Check if the file is empty
file_exists = os.path.exists(Climatic_data_pathway) and os.path.getsize(Climatic_data_pathway) > 0

try:
    with open(Climatic_data_pathway, mode='a', newline='') as csv_file:
        fieldnames = ['Date', 'Time', 'Zone', 'Subzone', 'PAR', 'Solar radiation', 'Temp', 'Humidity', 'CO2 conc']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header only if the file is empty
        if not file_exists:
            writer.writeheader()



        while True:
            date, time = get_datetime()

            try:
                # Read data from PAR_1
                PAR_intensity_1 = PAR_1.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "1", 'PAR': PAR_intensity_1})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading PAR_1 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from PAR_2
                PAR_intensity_2 = PAR_2.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "2", 'PAR': PAR_intensity_2})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading PAR_2 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from PAR_3
                PAR_intensity_3 = PAR_3.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "1", 'PAR': PAR_intensity_3})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading PAR_3 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from PAR_4
                PAR_intensity_4 = PAR_4.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "2", 'PAR': PAR_intensity_4})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading PAR_4 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from Solar_11
                Solar_Radiation_11 = Solar_11.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "1", 'Solar radiation': Solar_Radiation_11})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading Solar_11 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from Solar_12
                Solar_Radiation_12 = Solar_12.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "2", 'Solar radiation': Solar_Radiation_12})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading Solar_12 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from Solar_13
                Solar_Radiation_13 = Solar_13.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "1", 'Solar radiation': Solar_Radiation_13})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading Solar_13 at {now[1]} on {now[0]}: {e}")

            try:
                # Read data from Solar_14
                Solar_Radiation_14 = Solar_14.read_float(0, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "2", 'Solar radiation': Solar_Radiation_14})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading Solar_14 at {now[1]} on {now[0]}: {e}")

            try:
                carbon_conc_41 = carbo_41.read_float(1, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "1", 'CO2 conc': carbon_conc_41})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading carbo_41 at {now[1]} on {now[0]}: {e}")

            try:
                carbon_conc_42 = carbo_42.read_float(1, 3, 2, 0)
                sleep(1)
                writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "1", 'CO2 conc': carbon_conc_42})
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading carbo_42 at {now[1]} on {now[0]}: {e}")

            try:
                THUM_31.write("OPEN 31\r\n")
                THUM_31.flush()
                sleep(1)
                THUM_31.write("SEND\r\n")
                THUM_31.flush()
                sleep(1)
                data_31 = THUM_31.readlines()
                last_line_31 = data_31[-1]
                rh_index_31 = last_line_31.find('RH=')
                temp_index_31 = last_line_31.find("Ta=")
                if rh_index_31 != -1 and temp_index_31 != -1:
                    rh_value_31 = float(last_line_31[rh_index_31 + 3:last_line_31.find('%RH')])
                    temp_value_31 = float(last_line_31[temp_index_31 + 3:last_line_31.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "1", 'Temp': temp_value_31, 'Humidity': rh_value_31})
                sleep(1)
                THUM_31.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_31 at {now[1]} on {now[0]}: {e}")
                
            try:
                THUM_32.write("OPEN 32\r\n")
                THUM_32.flush()
                sleep(1)
                THUM_32.write("SEND\r\n")
                THUM_32.flush()
                sleep(1)
                data_32 = THUM_32.readlines()
                last_line_32 = data_32[-1]
                rh_index_32 = last_line_32.find('RH=')
                temp_index_32 = last_line_32.find("Ta=")
                if rh_index_32 != -1 and temp_index_32 != -1:
                    rh_value_32 = float(last_line_32[rh_index_32 + 3:last_line_32.find('%RH')])
                    temp_value_32 = float(last_line_32[temp_index_32 + 3:last_line_32.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'Zone': "B", 'Subzone': "2", 'Temp': temp_value_32, 'Humidity': rh_value_32})
                sleep(1)
                THUM_32.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_32 at {now[1]} on {now[0]}: {e}")

            try:
                THUM_33.write("OPEN 33\r\n")
                THUM_33.flush()
                sleep(1)
                THUM_33.write("SEND\r\n")
                THUM_33.flush()
                sleep(1)
                data_33 = THUM_33.readlines()
                last_line_33 = data_33[-1]
                rh_index_33 = last_line_33.find('RH=')
                temp_index_33 = last_line_33.find("Ta=")

                if rh_index_33 != -1 and temp_index_33 != -1:
                    rh_value_33 = float(last_line_33[rh_index_33 + 3:last_line_33.find('%RH')])
                    temp_value_33 = float(last_line_33[temp_index_33 + 3:last_line_33.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "1", 'Temp': temp_value_33, 'Humidity': rh_value_33})
                sleep(1)
                THUM_33.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_33 at {now[1]} on {now[0]}: {e}")

            try:
                THUM_34.write("OPEN 34\r\n")
                THUM_34.flush()
                sleep(1)
                THUM_34.write("SEND\r\n")
                THUM_34.flush()
                sleep(1)
                data_34 = THUM_34.readlines()
                last_line_34 = data_34[-1]
                rh_index_34 = last_line_34.find('RH=')
                temp_index_34 = last_line_34.find("Ta=")
                if rh_index_34 != -1 and temp_index_34 != -1:
                    rh_value_34 = float(last_line_34[rh_index_34 + 3:last_line_34.find('%RH')])
                    temp_value_34 = float(last_line_34[temp_index_34 + 3:last_line_34.find("'C")])
                    writer.writerow({'Date': date, 'Time': time, 'Zone': "C", 'Subzone': "2", 'Temp': temp_value_34, 'Humidity': rh_value_34})
                sleep(1)
                THUM_34.write("CLOSE\r\n")
                sleep(1)
            except Exception as e:
                now = get_datetime()
                print(f"Error reading THUM_34 at {now[1]} on {now[0]}: {e}")

except KeyboardInterrupt:
    # Close serial ports only if they are open
    if carbo_41.serial.is_open:
        carbo_41.serial.close()
    if carbo_42.serial.is_open:
        carbo_42.serial.close()

    if Solar_11.serial.is_open:
        Solar_11.serial.close()
    if Solar_12.serial.is_open:
        Solar_12.serial.close()
    if Solar_13.serial.is_open:
        Solar_13.serial.close()
    if Solar_14.serial.is_open:
        Solar_14.serial.close()

    if PAR_1.serial.is_open:
        PAR_1.serial.close()
    if PAR_2.serial.is_open:
        PAR_2.serial.close()
    if PAR_3.serial.is_open:
        PAR_3.serial.close()
    if PAR_4.serial.is_open:
        PAR_4.serial.close()

    print("Ports Closed")
