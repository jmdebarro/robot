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
        self.fd = None

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="oha{sv}", out_signature="")
    def NewConnection(self, device, fd, properties):
        print("New connection from:", device)
        self.fd = fd.take()

        # Set up GLib IO watch for non-blocking event-driven handling
        GLib.io_add_watch(self.fd, GLib.IO_IN, self.on_data)

    def on_data(self, fd, condition):
        try:
            data = os.read(fd, 1024)
            if not data:
                print("Client disconnected.")
                os.close(fd)
                return False  # Stop watching
            msg = data.decode('utf-8', errors='ignore').strip()
            print(f"Received: '{msg}'")
            msg += "\n"
            encoded_msg = msg.encode('utf-8')
            os.write(fd, encoded_msg)
        except Exception as e:
            print("Error during read/write:", e)
            os.close(fd)
            return False
        return True  # Continue watching

    @dbus.service.method("org.bluez.Profile1",
                         in_signature="o", out_signature="")
    def RequestDisconnection(self, device):
        print("RequestDisconnection")
        if self.fd:
            try:
                os.close(self.fd)
            except Exception:
                pass
            self.fd = None

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

# Make device discoverable and pairable
adapter_obj = bus.get_object("org.bluez", adapter_path)
adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")
adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Pairable", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(True))
adapter_props.Set("org.bluez.Adapter1", "Alias", dbus.String("RaspberryPi-BT"))

# Start the main loop
loop = GLib.MainLoop()
loop.run()
