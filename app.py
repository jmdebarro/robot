from flask import Flask, render_template, jsonify, request
import asyncio
from bleak import BleakClient

app = Flask(__name__)

ble_client = None

# UUIDs
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
CHARACTERISTIC_UUID = "12345678-1234-1234-1234-1234567890cd"


# Connecet to robot
async def connect():
    global ble_client
    ble_client = BleakClient("b8:27:eb:14:1a:19")
    print("Inside here")
    print(ble_client)
    await ble_client.connect()
    return ble_client.is_connected


# Disconnect from Robot
async def disconnect():
    global ble_client
    try:
        if ble_client and ble_client.is_connected:
            asyncio.run(ble_client.disconnect())
            return jsonify({"status": "Disconnected"})
    except Exception as e:
        return jsonify({"status" : "Failed", "message": str(e)}), 500    


# Send commands
async def send_command(command):
    global ble_client
    if ble_client and ble_client.is_connected:
        await ble_client.write_gatt_char(CHARACTERISTIC_UUID, command.encode())
        return True
    else:
        return False


# Renders HTML is template folder
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/command', methods=['POST'])
def command():
    data = request.json
    cmd = data["command"]

    if not cmd:
        return jsonify({'status': 'error', 'message': 'No command provided'}), 400
    try:
        success = asyncio.run(send_command(cmd))
        if success:
            return jsonify({'status': 'command sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Not connected'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Establishes connection with the robot
@app.route("/connect", methods=["POST"])
def link():
    try:
        connected_ble = asyncio.run(connect())
        return jsonify({"status" : "Connected" if connected_ble else "Failed"}), 400
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


@app.route('/disconnect', methods=['POST'])
def disconnect():
    global ble_client
    try:
        if ble_client and ble_client.is_connected:
            asyncio.run(ble_client.disconnect())
            return jsonify({'status': 'disconnected'})
        else:
            return jsonify({'status': 'not connected'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)