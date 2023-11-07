import serial
import time
import io
import csv
from datetime import datetime

THUM_240 = serial.Serial("/dev/ttyACM0",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False,
                   timeout=1)
#THUM_240 = io.TextIOWrapper(io.BufferedRWPair(THUM_240, THUM_240))

# Open the CSV file for writing
csv_file = open('sensor_data.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Date', 'Time', 'Humidity', 'Temperature'])

try:
    while True:
        THUM_240.write("R")
        data = THUM_240.readline()
        print(data)
    
        # Assuming the response format is "RH= 54.4 %RH Ta= 26.8 'C"
        parts = data.split()
        
        # Get current date and time
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')
        current_time = current_datetime.strftime('%H:%M:%S')  # Renamed variable to avoid conflict

        # Check if the response format is correct
        if len(parts) >= 6 and parts[0] == 'RH=' and parts[2] == '%RH' and parts[3] == 'Ta=' and parts[5] == "'C":
            # Extract humidity and temperature values
            humidity = float(parts[1])
            temperature = float(parts[4])

            # Log data to CSV
            csv_writer.writerow([date, current_time, humidity, temperature])

        else:
            # Log invalid response to CSV
            print(f"Invalid response format at {date} {current_time}")

        # Wait for 60 seconds (1 minute)
        time.sleep(5)

except KeyboardInterrupt:
    # Clean up when interrupted
    print("Ports Now Closed")
    csv_file.close()
