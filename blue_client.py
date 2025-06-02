import serial
import time

ser = serial.Serial('/dev/rfcomm0', baudrate=9600, timeout=1)

# Give it a moment to connect
time.sleep(2)

# Send a command
ser.write(b'ping\n')

# Read response
response = ser.readline()
print("Response from Pi:", response.decode().strip())

ser.close()
