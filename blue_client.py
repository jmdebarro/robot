import serial
import time

# For Linux: use '/dev/rfcomm0'
# For Windows: use 'COM5', 'COM6', etc.
port = 'COM7'  # or 'COM5'

try:
    ser = serial.Serial(port, baudrate=9600, timeout=1)
    time.sleep(1)  # Give it a second to settle

    # Send a command
    ser.write(b'ping\n')

    # Read the response
    response = ser.readline().decode().strip()
    print("Received:", response)

    ser.close()

except serial.SerialException as e:
    print("Could not open port:", e)
