import serial
import io
from time import sleep
from datetime import datetime

THUM_1 = serial.Serial("/dev/ttyACM0",
                   baudrate=4800,
                   bytesize=serial.SEVENBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=serial.STOPBITS_ONE,
                   xonxoff=False)
HUM_1 = io.TextIOWrapper(io.BufferedRWPair(THUM_1, THUM_1))
try:
    while True:
        HUM_1.write("send 1\n")
        HUM_1.flush()
        sleep(0.5)
        data=THUM_1.readline()
        print(f"{data}")
        HUM_1.flush()
        sleep(0.5)

except KeyboardInterrupt:
    # Clean up when interrupted
    print("Ports Now Closed")
