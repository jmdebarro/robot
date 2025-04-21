import asyncio
from bleak import BleakClient

# UUIDs
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
CHARACTERISTIC_UUID = "12345678-1234-1234-1234-1234567890cd"

async def run():
    async with BleakClient("b8:27:eb:14:1a:19") as client:
        print(f"Connected: {client.is_connected}")

        # Write a command (e.g., "forward")
        await client.write_gatt_char(CHARACTERISTIC_UUID, b"forward")
        print("Command sent")

        # Read the value
        value = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print(f"Received: {value}")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())