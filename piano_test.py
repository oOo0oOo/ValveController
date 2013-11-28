from usb_valves import Controller
import time

class PianoTest(object):
	'''
		Piano Sequence Test
	'''

	def __init__(self, controller):
		'''
			controller = instance of USBIO Controller
		'''
		self.controller = controller
		self.adresses = [('A', 1), ('A', 2), ('A', 3)]
		self.patterns = [
			[True, False, True],
			[True, False, False],
			[True, True, False],
			[False, True, False],
			[False, True, True],
			[False, False, True]
		]

	def run(self, delay, num_cycles = 1000):
		'''
			delay in ms
		'''
		delay = float(delay)/1000
		ad1, ad2, ad3 = self.adresses
		for i in range(num_cycles):
			for v1, v2, v3 in self.patterns:
				self.controller.set_state({ad1: v1, ad2: v2, ad3: v3})
				time.sleep(delay)

c = Controller('COM5')
c.add_all()
test = PianoTest(c)
test.run(10, 100)