from usb_valves import Controller
import time

# Example: 8 Valves always ON (closed) on port A
controller = Controller('COM3')

#Add all pins on all ports
controller.add_all()

# Cycle through all valves repeatedly
for i in range(25):
	# Cycle through each pin
	for pin in range(1,9):

		# Activate specific pin
		controller.activate('A', pin)

		# Wait 0.01 seconds
		time.sleep(0.01)

		# Deactivate pin
		controller.deactivate('A', pin)

controller.close()