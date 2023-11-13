import serial
import io
import threading
from time import sleep

def read_sensor(port, sensor_number):
    serial_sensor = serial.Serial(port,
                                  baudrate=4800,
                                  bytesize=serial.SEVENBITS,
                                  parity=serial.PARITY_EVEN,
                                  stopbits=serial.STOPBITS_ONE,
                                  xonxoff=False,
                                  timeout=5)
    hum_sensor = io.TextIOWrapper(io.BufferedRWPair(serial_sensor, serial_sensor))

    try:
        hum_sensor.write(f"open {sensor_number}\r\n")  # Open a connection to the sensor
        hum_sensor.flush()
        print(f"Sensor {sensor_number}: opened connection")
        sleep(5)  # Allow time for the sensor to initialize

        hum_sensor.write("R\r\n")  # Start continuous output
        hum_sensor.flush()
        print(f"Sensor {sensor_number}: started continuous output")
        sleep(2)  # Allow time for the sensor to start continuous output

        while True:
            hum_sensor.write("SEND\r\n")  # Request a reading
            hum_sensor.flush()
            data = hum_sensor.readline()
            print(f"Sensor {sensor_number}: data is {data}")

            # Optional: Stop continuous output if needed
            # hum_sensor.write("S\r\n")
            # hum_sensor.flush()

            sleep(5)  # Adjust as needed based on your interval requirements

    except KeyboardInterrupt:
        # Clean up when interrupted
        print(f"Sensor {sensor_number} Port Closed")
    finally:
        # Close the serial port to ensure clean termination
        serial_sensor.close()

# List of sensor numbers in the desired order
sensor_numbers = [1,0]

# Serial port for all sensors
port = "/dev/ttyACM0"

# Create threads for each sensor
threads = []
for sensor_number in sensor_numbers:
    thread = threading.Thread(target=read_sensor, args=(port, sensor_number))
    threads.append(thread)
    thread.start()
    sleep(5)

# Wait for all threads to complete
for thread in threads:
    thread.join()
