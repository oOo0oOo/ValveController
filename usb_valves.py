############################################################################
#
# Python Interface for Solenoid Valve Controller
# Oliver Dressler, 2013
#
############################################################################

from serial import Serial
from struct import pack,unpack
import time

class Controller(object):
	'''
		Interfaces with one USB I/O 24R Valve controller with up to 24 valves connected.
		Keeps track of current state and default state of all valves.
		Inspired by: https://code.google.com/p/python-usbio24/
	'''

	def __init__(self, device = 'COM3'):
		'''
			Initialize serial connection to usbio module.
			Set all pins to output mode & initialize default state.
		'''
		# Init serial connection with usbio and set mode 1
		self.usbio = Serial(device, timeout= 1)
		self.usbio.write(pack('B', 1))

		self.default_state = {}
		self.current_state = {}

		# Put all pins to output mode
		for port in ['A', 'B', 'C']:
			cmd = pack('ccB', '!', port, 0)
			self.usbio.write(cmd)

		print 'Successfully connected to {} on {}.'.format(self.identify(), device)

	def close(self):
		'''
			Resets all valves to default and closes the serial connection.
		'''
		self.reset()
		self.usbio.close()

	def identify(self):
		'''
			Request's the device's "identity." Expect a newline-terminated response similar
			to "USB I/O 24" (directly copied from: https://code.google.com/p/python-usbio24/)
		'''
		self.usbio.write('?')
		return self.usbio.readline().strip()

	def _parse_pin_num(self, port, pin):
		'''
			Get pin number for port, pin combo.
		'''
		if port == 'A': num = 0
		elif port == 'B': num = 8
		elif port == 'C': num = 16
		return num + (pin - 1)

	def _set_pin_high(self, port, pin):
		'''
			Set a pin output to high. Use activate to controll directly, 
			which also updates the current state...
		'''
		cmd = pack('cB', 'H', self._parse_pin_num(port, pin))
		self.usbio.write(cmd)

	def _set_pin_low(self, port, pin):
		'''
			Set a pin output to low. Use deactivate to controll directly, 
			which also updates the current state...
		'''
		cmd = pack('cB', 'L', self._parse_pin_num(port, pin))
		self.usbio.write(cmd)

	def add_valves(self, default_states):
		'''
			Adds a set of valves and their default state.
			E.g. default_states = {('A', 1): True, ('A', 2): True}
		'''
		self.default_state.update(default_states)
		self.current_state.update(default_states)
		self.reset_default()

	def add_port(self, port, default = False):
		'''
			Adds all valves on a port.
		'''
		defaults = {}
		for pin in range(1,9):
			defaults[(port, pin)] = default

		self.add_valves(defaults)

	def add_all(self, default = False):
		'''
			Add all 24 valves (on 3 ports) on the controller.
		'''
		for port in ['A', 'B', 'C']:
			self.add_port(port, default)

	def remove_valves(self, adresses):
		'''
			Removes valves, accepts list of adresses.
			E.g. adresses = [('A', 1), ('A', 2)]
		'''
		for ad in adresses:
			try:
				del self.default_state[ad]
				del self.current_state[ad]
			except KeyError:
				pass

	def remove_port(self, port):
		all_ad = self.default_state.keys()
		self.remove_valves([ad for ad in all_ad if ad[0] == port])

	def remove_all(self):
		self.remove_valves(self.default_state.keys())

	def set_state(self, state):
		'''
			Set state of all valves on all ports.
			E.g. states = {('A', 1): False, ('A', 2): True}
		'''
		for adress, st in state.items():
			if st != self.current_state[adress]:
				self.current_state[adress] = st

		state_nums = {'A': 0, 'B': 0, 'C': 0}
		for (port, pin), st in self.current_state.items():
			num = 0
			if st: num = 2 ** (pin - 1)
			state_nums[port] += num

		for port, num in state_nums.items():
			self.usbio.write(pack('cB', port, num))

	def set_states(self, states, timeout = 0.1, repetitions = 1):
		'''
			Accepts a list of states and cycles through them, 
			waiting timeout seconds in between states.
		'''
		for i in range(repetitions):
			for state in states:
				self.set_state(state)
				time.sleep(timeout)

	def activate(self, port, pin):
		'''
			Activate a single pin/valve.
		'''
		adress = (port, pin)
		if not self.current_state[adress]:
			self.current_state[adress] = True
			self._set_pin_high(port, pin)

	def deactivate(self, port, pin):
		'''
			Deactivate a single pin/valve.
		'''
		adress = (port, pin)
		if self.current_state[adress]:
			self.current_state[adress] = False
			self._set_pin_low(port, pin)

	def toggle(self, port, pin):
		'''
			Toggle single pin/valve.
		'''
		adress = (port, pin)
		if self.current_state[adress]:
			self._set_pin_low(port, pin)
		else:
			self._set_pin_high(port, pin)

		self.current_state[adress] = not self.current_state[adress]

	def reset(self):
		'''
			Resets all valves to their default states, then removes them.
		'''
		self.reset_default()
		self.remove_valves(self.default_state.keys())

	def reset_default(self):
		'''
			Resets all valves to their default state.
		'''
		self.set_state(self.default_state)



class PeristalticPump(object):
	'''
		Controlls a microfluidic peristaltic pump made up from three valves.
	'''

	default_patterns = [
		[True, False, True],
		[True, False, False],
		[True, True, False],
		[False, True, False],
		[False, True, True],
		[False, False, True]
	]

	def __init__(self, controller, adresses, patterns = False):
		'''
			controller = instance of USBIO Controller
			adresses = list of three adresses of valves in order of positive flow.
			patterns = patterns other than default patterns
				(according to Unger et al. (2000): http://www.sciencemag.org/content/288/5463/113.full)
		'''
		self.controller = controller
		self.adresses = adresses
		if patterns:
			self.patterns = patterns
		else:
			self.patterns = default_patterns

	def pump(self, num_cycles, frequency):
		'''
			One cycle corresponds to one run through all pattern.
			frequency is the frequency of pattern changes [Hz].
		'''
		delay = 1.0/frequency
		ad1, ad2, ad3 = self.adresses
		for i in range(num_cycles):
			for v1, v2, v3 in self.patterns:
				self.controller.set_state({ad1: v1, ad2: v2, ad3: v3})
				time.sleep(delay)