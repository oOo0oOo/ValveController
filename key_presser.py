from msvcrt import getch
from usb_valves import Controller
import time

port = raw_input('Which COM port is the Controller connected to?\n')
port = 'COM' + port

try:
    controller = Controller(port)
except Exception, e:
    raw_input(e)
    import sys
    sys.exit()

# Add all pins on all ports (default: all valves off)
controller.add_all(default=False)

# Map key presses to valves (48 -> 0, ..., 57 -> 9)
# Pump 0 doesn't exist will be mapped to reset all valves to default state.
key_map = {}
for p in range(9):
    key_map[p + 48] = ('A', p)

print 'Waiting for key presses...\nUse 1-8 for valves and 0 to reset all valves to the default state.'

while True:
    key = ord(getch())

    if key == 27:  # ESC stops program
        break

    # Check if any of the mapped keys is pressed
    valve = -1
    for k, p in key_map.items():
        if key == k:
            port, valve = p
            break

    if valve == 0:
        controller.reset_default()
        print 'Reset all valves to default state.'
    elif valve > 0:
        # Toggle valve
        controller.toggle(port, valve)
        print 'Toggled valve: {} {}'.format(port, valve)

controller.close()
