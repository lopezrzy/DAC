import serial
import io
from time import sleep

def initialize_sensor(port, sensor_number):
    serial_sensor = serial.Serial(port,
                                  baudrate=4800,
                                  bytesize=serial.SEVENBITS,
                                  parity=serial.PARITY_EVEN,
                                  stopbits=serial.STOPBITS_ONE,
                                  xonxoff=False,
                                  timeout=20)
    hum_sensor = io.TextIOWrapper(io.BufferedRWPair(serial_sensor, serial_sensor))

    try:
        while True:
            hum_sensor.write("R\r\n")  # Start continuous output
            hum_sensor.flush()
            print(f"Sensor {sensor_number}: started continuous output")
            sleep(2)  # Allow time for the sensor to start continuous output

            hum_sensor.write("SEND\r\n")  # Request a reading
            hum_sensor.flush()
            data = hum_sensor.readline().strip()
            print(f"Sensor {sensor_number}: data is {data}")

            # Optional: Stop continuous output if needed
            # hum_sensor.write("S\r\n")
            # hum_sensor.flush()

            sleep(5)  # Adjust as needed based on your interval requirements

    except KeyboardInterrupt:
        # Clean up when interrupted
        print(f"Sensor {sensor_number} Port Closed")

# List of sensor numbers in the desired order
sensor_numbers = [0]

# Serial port for all sensors
port = "/dev/ttyACM0"

# Loop through the sensors
for sensor_number in sensor_numbers:
    initialize_sensor(port, sensor_number)
