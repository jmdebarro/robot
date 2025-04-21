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
    # 1) Grab the first Bluetooth adapter (hci0)
    ble_adapter = adapter.Adapter()
    ble_adapter.powered = True

    # 2) Create a Peripheral
    robot = peripheral.Peripheral(adapter=ble_adapter,
                                  local_name='MyRobot',  # your device name
                                  appearance=0)

    # 3) Add a primary service
    robot.add_service(svc_id=1,
                      uuid=SERVICE_UUID,
                      primary=True)

    # 4) Add a characteristic under that service
    robot.add_characteristic(svc_id=1,
                             chr_id=1,
                             uuid=CHARACTERISTIC_UUID,
                             value=[],         # initial empty value
                             notifying=False,
                             flags=['read', 'write'],
                             read_callback=read_callback,
                             write_callback=write_callback)

    # 5) Publish (this starts advertising + GATT server)
    robot.publish()
    print("Advertising and GATT server running…")
    # 6) Sit in the main loop
    robot.run()

if __name__ == '__main__':
    main()