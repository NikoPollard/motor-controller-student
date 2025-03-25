from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket
import io

button_map = {
    ButtonPacket.BUTTON_1: "1",
    ButtonPacket.BUTTON_2: "2",
    ButtonPacket.BUTTON_3: "3",
    ButtonPacket.BUTTON_4: "4",
    ButtonPacket.UP: "UP",
    ButtonPacket.DOWN: "DOWN",
    ButtonPacket.LEFT: "LEFT",
    ButtonPacket.RIGHT: "RIGHT",
}

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

def setup(name):
    ble.name = name

def connect():
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    # Now we're connected
    print("Connected!")
    
def connected():
    return ble.connected

def write(msg):
    uart.write(msg.encode())
    
def read(in_wait):
    return uart.read(in_wait)
    
def in_waiting():
    return uart.in_waiting

# I don't use this method but you could use it to get button presses
# from the control pad
def button_press(data):
    packet = Packet.from_stream(io.BytesIO(data))
    if isinstance(packet, ButtonPacket) and packet.pressed:
        packet = Packet.from_stream(io.BytesIO(data))
        if packet.button in button_map:
            print(f"{button_map[packet.button]} button pressed!")
            return button_map[packet.button]

    return None