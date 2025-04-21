from bluezero import adapter, peripheral

SERVICE_UUID         = '12345678-1234-1234-1234-1234567890ab'
CHARACTERISTIC_UUID  = '12345678-1234-1234-1234-1234567890cd'

def write_callback(value, options):
    cmd = bytes(value).decode()
    print(f"BLE write received: {cmd}")
    # TODO: hook into your servo logic here

def read_callback(options):
    # Optionally return a status or sensor reading
    return bytearray("OK", 'utf-8')

def main():
    # 2) Create a Peripheral
    ble_adapter = adapter.Adapter()          # defaults to hci0
    ble_adapter.powered = True

    # ✅ Pass the adapter’s address string as the first argument:
    robot = peripheral.Peripheral(
        ble_adapter.address,
        local_name='MyRobot',
        appearance=0
    )

    # 3) Add a primary service
    robot.add_service(1, uuid=SERVICE_UUID, primary=True)

    # 4) Add a characteristic under that service
    robot.add_characteristic(1, 1, CHARACTERISTIC_UUID, False
                            ['read', 'write'], [],
                            read_callback=read_callback,
                            write_callback=write_callback)


    # 5) Publish (this starts advertising + GATT server)
    robot.publish()
    print("Advertising and GATT server running…")
    # 6) Sit in the main loop
    robot.run()

if __name__ == '__main__':
    main()