from msvcrt import getch, kbhit
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


# Periodically switch specific valve on/off
periodic_adress = ('A', 1)
periodic_off = 1
periodic_on = 1
periodic_state = False
last_switch = time.time()


while True:
    # Periodic Valve Switch
    cur_time = time.time()
    if not periodic_state and last_switch + periodic_off < cur_time:
        last_switch = cur_time
        periodic_state = True
        controller.activate(*periodic_adress)


    elif periodic_state and last_switch + periodic_on < cur_time:
        last_switch = cur_time
        periodic_state = False
        controller.deactivate(*periodic_adress)

    if kbhit():
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
            
            # Print a nice message
            if controller.current_state[(port, valve)]:
                state = 'ON'
            else:
                state = 'OFF'
            print 'Valve {} {}: {}'.format(port, valve, state)
        
controller.close()