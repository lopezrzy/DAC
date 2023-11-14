import serial
import io
from time import sleep
from datetime import datetime

def read_device(serial_wrapper, device_number):
    try:
        # Open the device
        serial_wrapper.write(f"OPEN {device_number}\r\n")
        serial_wrapper.flush()
        print(f"Device {device_number} is opened")
        sleep(5)
        
        hum_sensor.write("R\r\n")  # Start continuous output
        hum_sensor.flush()
        print(f"Sensor {sensor_number}: started continuous output")
        sleep(2)  # Allow time for the sensor to start continuous output

        # Send the data request
        serial_wrapper.write("SEND\r\n")
        serial_wrapper.flush()
        print("Send")
        sleep(10)

        # Read and print the data
        data = serial_wrapper.readlines()
        print(f"Data from Device {device_number}: {data}")
        sleep(3)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print(f"Ctrl+C received. Closing Device {device_number}")
    finally:
        # Close the device
        serial_wrapper.write("CLOSE\r\n")
        serial_wrapper.flush()
        print(f"Device {device_number} closed")
        sleep(5)

# Serial Configuration for Device 0
serial_THUM_0 = serial.Serial("/dev/ttyACM0",
                               baudrate=4800,
                               bytesize=serial.SEVENBITS,
                               parity=serial.PARITY_EVEN,
                               stopbits=serial.STOPBITS_ONE,
                               xonxoff=False,
                               timeout=2)
THUM_0 = io.TextIOWrapper(io.BufferedRWPair(serial_THUM_0, serial_THUM_0))


try:
    # Read from Device 0
    read_device(THUM_0, "0")


except KeyboardInterrupt:
    # Clean up when interrupted
    print("Ports Now Closed")
finally:
    # Close all open ports
    serial_THUM_0.close()
