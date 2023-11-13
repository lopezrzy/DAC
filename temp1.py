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
            hum_sensor.write(f"open {sensor_number}\r\n")
            hum_sensor.flush()
            print(f"Sensor {sensor_number}: open")
            sleep(1)
            hum_sensor.write("send\r\n")
            hum_sensor.flush()
            print(f"Sensor {sensor_number}: send")
            sleep(1)
            data = hum_sensor.readline().strip()
            hum_sensor.flush()
            #dataInString=str(data)
            print(f"Sensor {sensor_number}: data is {data}")
            sleep(1)
            hum_sensor.write("close\r\n")
            hum_sensor.flush()
            print(f"Sensor {sensor_number}: close")
            sleep(2)

    except KeyboardInterrupt:
        # Clean up when interrupted
        print(f"Sensor {sensor_number} Port Closed")

# List of sensor numbers in the desired order
#sensor_numbers = [31, 32, 33, 34]
sensor_numbers = [0]

# Serial port for all sensors
port = "/dev/ttyACM0"

# Loop through the sensors
for sensor_number in sensor_numbers:
    initialize_sensor(port, sensor_number)
