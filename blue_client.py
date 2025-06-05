import serial


ser = serial.Serial('COM7', baudrate=9600)  # baudrate is ignored for BT SPP
command = "start"
while(command != "stop"):
    command = input() + "\n"
    byte_command = command.encode('utf-8')
    ser.write(byte_command)
    response = ser.readline()  # assuming the Pi echoes a line
    print("Got reply:", response.decode())
ser.close()

