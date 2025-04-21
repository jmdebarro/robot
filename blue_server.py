import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib



BLUEZ_SERVICE_NAME       = 'org.bluez'
ADAPTER_IFACE            = 'org.bluez.Adapter1'
ADVERTISING_MANAGER_IFACE= 'org.bluez.LEAdvertisingManager1'
ADVERTISEMENT_IFACE      = 'org.bluez.LEAdvertisement1'
ADAPTER_PATH             = '/org/bluez/hci0'
ADVERTISEMENT_PATH       = '/org/bluez/robot/advertisement0'

class Advertisement(dbus.service.Object):
    def __init__(self, bus, path, service_uuids):
        super().__init__(bus, path)
        self.service_uuids = service_uuids

    @dbus.service.property(ADVERTISEMENT_IFACE, signature='s')
    def Type(self):
        return 'peripheral'

    @dbus.service.property(ADVERTISEMENT_IFACE, signature='as')
    def ServiceUUIDs(self):
        return self.service_uuids

    @dbus.service.method(ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print(f"{ADVERTISEMENT_PATH}: released")


# BlueZ GATT UUIDs
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"  # A custom UUID for your service
CHARACTERISTIC_UUID = "12345678-1234-1234-1234-1234567890cd"  # A custom UUID for the characteristic

class GATTCharacteristic(dbus.service.Object):
    """GATT Characteristic class to handle read and write operations"""
    
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)
        self.value = dbus.Array([], signature='y')  # Empty byte array as default value

    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties", in_signature="s", out_signature="y")
    def ReadValue(self, options):
        """Handle read requests from the client"""
        print("Read characteristic value:", self.value)
        return self.value

    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties", in_signature="ay", out_signature="s")
    def WriteValue(self, value):
        """Handle write requests from the client"""
        print("Received write command:", value)
        self.value = dbus.Array(value, signature='y')
        return "Success"

class GATTService(dbus.service.Object):
    """GATT Service class to handle service and characteristics"""
    
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)
        self.characteristic = GATTCharacteristic(bus, "/org/bluez/robot/drive")

    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties", in_signature="", out_signature="")
    def StartAdvertising(self, bus):
        """Start advertising the service"""
        
        # Create an advertisement object and start advertising
        advertisement = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/robot/advertisement1'), 'org.bluez.LEAdvertisement1')
        advertisement.StartAdvertising()
        print("Started advertising...")
def main():
    # 1) set up the D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # 2) Create and register your GATT service object
    service = GATTService(bus, '/org/bluez/robot/service0')

    # 3) Create advertisement object
    ad = Advertisement(bus, ADVERTISEMENT_PATH, ['12345678-1234-1234-1234-1234567890ab'])

    # 4) Register the advertisement
    ad_mgr = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, ADAPTER_PATH),
        ADVERTISING_MANAGER_IFACE
    )
    ad_mgr.RegisterAdvertisement(ADVERTISEMENT_PATH, {})

    print("Advertising started…")
    GLib.MainLoop().run()

if __name__ == "__main__":
    main()
