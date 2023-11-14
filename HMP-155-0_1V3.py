import serial
import io
from time import sleep

def open_device(serial_wrapper, device_number):
    # Open the device
    serial_wrapper.write(f"OPEN {device_number}\r\n")
    serial_wrapper.flush()
    print(f"Device {device_number} is opened")
    sleep(2)
        
def read_device(serial_wrapper, device_number):
    try:
        # Send the data request
        serial_wrapper.write("SEND\r\n")
        serial_wrapper.flush()
        print("Send")
        sleep(5)
        # Read and print the data
        data = serial_wrapper.readline().strip()
        print(f"Data from Device {device_number}: {data}")
        sleep(3)

    except KeyboardInterrupt:
        # Clean up when interrupted
        serial_sensor.write("close\r\n")
        print(f"Sensor {sensor_number}: close")
        print(f"Sensor {sensor_number} Port Closed")
        serial_sensor.close()

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

for i, device_number in enumerate(device_numbers):
    open_device(THUM_devices[i], device_number)

try:
    while True:
        for i, device_number in enumerate(device_numbers):
            read_device(THUM_devices[i], device_number)

except KeyboardInterrupt:
    # Clean up when interrupted
    print("Ports Now Closed")
finally:
    # Close all open ports
    for serial_device in serial_devices:
        serial_device.close()
