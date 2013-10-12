import unittest
import usb_valves
import time

port = 'COM3'

class TestUSBValves(unittest.TestCase):

	def setUp(self):
		self.cont = usb_valves.Controller(port)
		self.cont.add_all()

		# Test new instance
		self.assertTrue(isinstance(self.cont, usb_valves.Controller))
		self.assertTrue(self.cont.identify())


	def tearDown(self):
		# Also tests closing the controller
		self.cont.close()

		self.assertRaises(KeyError, self.cont.activate, 'A', 1)


	def test_add_remove(self):
		# All
		try:
			self.cont.activate('A', 1)
		except Exception, e:
			self.fail(e)

		self.cont.remove_all()
		self.assertRaises(KeyError, self.cont.activate, 'A', 1)

		# Port
		for port in ['A', 'B', 'C']:
			self.cont.add_port(port)
			try:
				self.cont.activate(port, 1)
			except Exception, e:
				self.fail(e)

			self.cont.remove_port(port)
			self.assertRaises(KeyError, self.cont.activate, 'A', 1)

		# Pin (valves)
		for port in ['A', 'B', 'C']:
			for pin in range(1,9):
				adr = (port, pin)
				self.cont.add_valves({adr: False})
				try:
					self.cont.activate(port, pin)
				except Exception, e:
					self.fail(e)

				self.cont.remove_valves([adr])
				self.assertRaises(KeyError, self.cont.activate, 'A', 1)


	def test_activate_deactivate(self):
		# Cycle through all valves (once, slow)
		for pin in range(1,9):
			self.cont.activate('A', pin)
			time.sleep(0.15)
			self.cont.deactivate('A', pin)
		
		# Cycle through all valves (20 times fast)
		for i in range(20):
			for pin in range(1,9):
				self.cont.activate('A', pin)
				time.sleep(0.01)
				self.cont.deactivate('A', pin)


	def test_parallel_switching(self):
		'''
			Switches all valves in parallel.
		'''
		# Create the state all_open 
		all_open = {}
		for p in ['A', 'B', 'C']:
			for pin in range(1,9):
				all_open[(p, pin)] = True

		for i in range(20):
			# Set state all open
			self.cont.set_state(all_open)
			time.sleep(0.05)
			# Reset to default state
			self.cont.reset_default()
			time.sleep(0.05)


if __name__ == '__main__':
	unittest.main()
