from flask import Flask, render_template, jsonify, request
import asyncio
from bleak import BleakClient

app = Flask(__name__)

ble_client = None

# UUIDs
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
CHARACTERISTIC_UUID = "12345678-1234-1234-1234-1234567890cd"

# Start event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# Connecet to robot
async def connect():
    global ble_client
    ble_client = BleakClient("b8:27:eb:14:1a:19")
    await ble_client.connect()
    return ble_client.is_connected


# Disconnect from Robot
async def disconnect():
    global ble_client
    try:
        if ble_client and ble_client.is_connected:
            loop.run_until_complete(ble_client.disconnect())
            return jsonify({"status": "Disconnected"})
    except Exception as e:
        return jsonify({"status" : "Failed", "message": str(e)}), 500    


# Send commands
async def send_command_ble(command):
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
        success = loop.run_until_complete(send_command_ble(cmd))
        if success:
            return jsonify({'status': 'command sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Not connected'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Establishes connection with the robot
@app.route("/start_robot", methods=["POST"])
def start_robot():
    try:
        connected_ble = loop.run_until_complete(connect)
        return jsonify({"status" : "Connected" if connected_ble else "Failed"}), 400
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


@app.route('/disconnect', methods=['POST'])
def disconnect():
    global ble_client
    try:
        if ble_client and ble_client.is_connected:
            loop.run_until_complete(ble_client.disconnect())
            return jsonify({'status': 'disconnected'})
        else:
            return jsonify({'status': 'not connected'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)