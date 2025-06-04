import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import os

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

adapter_path = "/org/bluez/hci0"
profile_path = "/bluez/example/profile"

# Create a basic SPP UUID
SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"

class Profile(dbus.service.Object):
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method("org.bluez.Profile1",
                        in_signature="oha{sv}", out_signature="")
    def NewConnection(self, device, fd, properties):
        print("New connection from:", device)
        
        # Open the file descriptor as a read-write file
        sock = os.fdopen(fd.take(), 'r+b', buffering=0)
        
        while True:
            try:
                line = sock.readline().decode('utf-8').strip()
                print(f"Received: '{line}'")
                
                if line == "ping":
                    sock.write(b"pong\n")
                else:
                    sock.write(b"unknown\n")
            except Exception as e:
                print("Connection error:", e)
                break

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="o", out_signature="")
    def RequestDisconnection(self, device):
        print("RequestDisconnection")

# Register Profile with BlueZ
profile_options = {
    "Name": "SerialPort",
    "Service": "spp",
    "Role": "server",
    "Channel": dbus.UInt16(1),
    "RequireAuthentication": dbus.Boolean(False),
    "RequireAuthorization": dbus.Boolean(False),
    "AutoConnect": dbus.Boolean(True),
    "UUIDs": dbus.Array([SPP_UUID], signature="s")
}

profile = Profile(bus, profile_path)
manager = dbus.Interface(
    dbus.SystemBus().get_object("org.bluez", "/org/bluez"),
    "org.bluez.ProfileManager1"
)

# Register the SPP profile
manager.RegisterProfile(profile_path, SPP_UUID, profile_options)
print("SPP profile registered on channel 1")

# Make device discoverable and pairable using org.freedesktop.DBus.Properties
adapter_obj = bus.get_object("org.bluez", "/org/bluez/hci0")
adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")
adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Pairable", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Alias", dbus.String("RaspberryPi-BT"))

# Start the main loop
loop = GLib.MainLoop()
loop.run()
