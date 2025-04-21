import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

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
    def WriteValue(self, value, options):
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
    def StartAdvertising(self):
        """Start advertising the service"""
        adapter = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'), 'org.freedesktop.DBus.Properties')
        adapter.StartAdvertising()
        print("Started advertising...")

def main():
    # Initialize the DBus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    bus = dbus.SystemBus()
    bus.request_name("org.bluez.example")
    
    # Create service and characteristic
    service = GATTService(bus, "org/bluez/robot/drive")
    
    # Start advertising
    service.StartAdvertising()
    
    # Start the main loop to listen for DBus events
    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()
