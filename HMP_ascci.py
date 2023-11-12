import serial
import io
from time import sleep
from datetime import datetime

THUM_34 = serial.Serial("/dev/ttyACM0",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False,
                   timeout=2)

HUM_34 = io.TextIOWrapper(io.BufferedRWPair(THUM_34, THUM_34))

try:
    while True:
        HUM_34.write("open 0")
        print("open")
        HUM_34.flush()
        sleep(1)
        HUM_34.write("send")
        print("send")
        HUM_34.flush()
        sleep(1)
        data = HUM_34.readline()
        print(f"data is: {data}")
        HUM_34.flush()
        sleep(1)
        HUM_34.write("close")
        print("close")
        sleep(2)
      
except KeyboardInterrupt:
    # Clean up when interrupted
    print("Ports Now Closed")
