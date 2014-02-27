#-------------------------------------------------
#
# Python Tutorial Session 6
# (c) Oliver Dressler, 2014
#
#-------------------------------------------------


####
# Solenoid Valve Control
####

import time
from serial import Serial
from struct import pack


def prepare_controller(port = 'COM5'):
	## To open a new serial connection we have to know the port
	## our device is connected to...
	connection = Serial(port)


	## how does a command for the controller look like:
	## pack creates a string with all arguments packed as
	## specified using the first argument ('B' in this case means Byte)
	cmd  = pack('B', 1)
	# print repr(cmd), cmd

	## This command puts all pins in output mode
	## Now we just need to send it to the connected controller
	connection.write(cmd)


	## Now we have to put all the pins in output mode
	for port in ['A', 'B', 'C']:
		cmd = pack('ccB', '!', port, 0)
		connection.write(cmd)

	return connection

connection = prepare_controller()

## To adress individual pins the controller uses a numbering system
## Here is a translation function
def get_pin_num(port, pin):
	''' 
		Pin can be 1-8, port can be A, B or C.
		Pins on port A are numbered 0-7, B are 8-15 and C are 16-23
	'''
	if port not in ('A', 'B', 'C') or pin not in range(1, 9):
		raise RuntimeError('Invalid Port or Pin...')

	if port == 'A': num = 0
	elif port == 'B': num = 8
	elif port == 'C': num = 16
	return num + (pin - 1)

# print get_pin_num('A', 1), get_pin_num('B', 1), get_pin_num('C', 8)


## Two functions to turn pin high (activate valve) or low
def set_pin_high(port, pin):
	## Construct command
	cmd = pack('cB', 'H', get_pin_num(port, pin))
	# print cmd, repr(cmd)
	connection.write(cmd)

def set_pin_low(port, pin):
	## Construct command
	cmd = pack('cB', 'L', get_pin_num(port, pin))
	# print cmd, repr(cmd)
	connection.write(cmd)


for i in xrange(50):
	set_pin_high('A', 1)
	time.sleep(0.025)
	set_pin_low('A', 1)
	time.sleep(0.025)


## Always close a serial connection when you're done
connection.close()


