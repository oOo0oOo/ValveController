from usb_valves import Controller
import time

class PianoTest(object):
	'''
		Piano Sequence Test
	'''

	def __init__(self, controller):
		'''
			controller = instance of USBIO Controller
			adresses = list of three adresses of valves in order of positive flow.
			patterns = patterns other than default patterns
				(according to Unger et al. (2000): http://www.sciencemag.org/content/288/5463/113.full)
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
			One cycle corresponds to one run through all pattern.
			frequency is the frequency of pattern changes [Hz].
		'''
		ad1, ad2, ad3 = self.adresses
		for i in range(num_cycles):
			for v1, v2, v3 in self.patterns:
				self.controller.set_state({ad1: v1, ad2: v2, ad3: v3})
				time.sleep(delay)

c = Controller('COM4')
c.add_all()
test = PianoTest(c)
test.run(10)