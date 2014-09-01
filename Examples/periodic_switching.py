from msvcrt import getch, kbhit
from usb_valves import Controller
import time

# Connect to the controller using the Controller class from usb_valves
port = raw_input('Which COM port is the Controller connected to?\n')
port = 'COM' + port

try:
    controller = Controller(port)
except Exception, e:
    raw_input(e)
    import sys
    sys.exit()


# Add all pins on all ports (default: all valves off)
default = False
controller.add_all(default=default)


# Map key presses to valves (48 -> 0, ..., 57 -> 9)
# Pump 0 doesn't exist will be mapped to reset all valves to default state.
key_map = {}
for p in range(9):
    key_map[p + 48] = ('A', p)


# Periodically switch specific valve on/off
periodic_adress = ('A', 1)
periodic_off = 0.1               # [s]
periodic_on = 0.1                # [s]


# Keep track of state...
periodic_state = False
last_switch = time.time()
switching = False                   # Switching enabled otherwise permanently closed...


# Let's go!!
print '''
Waiting for key presses...
Use . to enable periodic switching of valve 1.
Use 1-8 for valves and 0 to reset all valves to the default state ({}).
Press ESC to end program.
'''.format(default)

while True:
    # Periodic Valve Switch
    cur_time = time.time()
    if switching and not periodic_state and last_switch + periodic_off < cur_time:
        last_switch = cur_time
        periodic_state = True
        controller.activate(*periodic_adress)

    elif periodic_state and last_switch + periodic_on < cur_time:
        last_switch = cur_time
        periodic_state = False
        controller.deactivate(*periodic_adress)

    # React to pressed keys
    if kbhit():
        key = ord(getch())
        
        if key == 27:  # ESC stops program
            break

        # use . to toggle periodic switching
        elif key == 46:
            switching = not switching
            msg = 'Periodic Switching: ' + str(switching)
            if not switching:
                msg += '; Valve currently ON: ' + str(controller.current_state[periodic_adress])
            print msg

        # Check if any of the mapped keys (1-8) is pressed
        valve = -1
        for k, p in key_map.items():
            if key == k:
                port, valve = p
                break

        if valve == 0:
            controller.reset_default()
            print 'Reset all valves to default state ({}).'.format(default)

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