from pydbus import SystemBus
from gi.repository import GLib
import dbus
import dbus.service
import os

bus = SystemBus()
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
        os.dup2(fd.take(), 0)
        os.dup2(fd.take(), 1)
        while True:
            try:
                data = input()
                if data.strip() == "ping":
                    print("pong")
                else:
                    print("unknown")
            except EOFError:
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

profile = Profile(bus.con, profile_path)
manager = dbus.Interface(
    dbus.SystemBus().get_object("org.bluez", "/org/bluez"),
    "org.bluez.ProfileManager1"
)

manager.RegisterProfile(profile_path, SPP_UUID, profile_options)
print("SPP profile registered on channel 1")

# Make device discoverable/pairable
adapter = bus.get("org.bluez", adapter_path)
adapter.Powered = True
adapter.Discoverable = True
adapter.Pairable = True
adapter.Alias = "RaspberryPi-BT"

loop = GLib.MainLoop()
loop.run()
