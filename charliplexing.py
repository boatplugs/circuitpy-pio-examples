# raspberry pi charlieplexing pio example with circuitpython
# big thanks to pierremolinaro for the great writeup and detail
# https://github.com/pierremolinaro/rp2040-charlieplexing/blob/main/extras/rp2040-charlieplexing.pdf

import array
import time
import board
import rp2pio
import adafruit_pioasm
from digitalio import DigitalInOut, Direction, Pull, DriveMode


pins = {0: board.GP0,
		1: board.GP1,
		2: board.GP2,}


# this pio program will iterate through each set of 3x3 bits and turn on the corresponding GPIO bitmask style
pio_solid = '''
.program sequence
.wrap_target
	pull noblock
	mov x, osr
main:
	out pindirs, 3 		; set the pin direction off the first 3 bits
	out pins, 3 		; set the first led pair pin high from the next 3 bits
	out pins, 3 		; set the second led pair pin high from the final 3 bits
	set pins, 0 		; set all pins to input
	jmp !osre main 		; if our output shift register is not null loop and repeat for each remaining sets of bits
.wrap
'''

# this pio program will iterate through each set of 3x3 bits and turn on the corresponding GPIO bitmask style then turn it off
pio_flicker = '''
.program sequence
.wrap_target
	pull noblock
	mov x, osr
main:
	out pindirs, 3
	out pins, 3
	set pins, 0
	out pins, 3
	set pins, 0
	jmp !osre main
.wrap
'''


pioc_solid = adafruit_pioasm.assemble(pio_solid)
pioc_flicker = adafruit_pioasm.assemble(pio_flicker)


class array_sm():
		def __init__(self, array_pins, program):
			self.program = program
			self.start_pin = array_pins[0]
			self.pins_count = array_pins[1]
			self.sm = rp2pio.StateMachine(
				self.program,
				frequency=6000,
				first_out_pin=self.start_pin,
				out_pin_count=self.pins_count,
				first_set_pin=self.start_pin,
				set_pin_count=self.pins_count,
				out_shift_right=False,
				exclusive_pin_use=False			# necessary to prevent our two statemachines from locking eachother
				)

		def write(self, array_bytes):

			# we're going to start with a base value of zero then bitshift in the bit data required
			data = 0
			for i in array_bytes:
				data = data | (i << 0)
				data <<= 3
			data <<= 2

			# convert that data into an array of 32-bit integers
			array_config = array.array('I', [data])
			print(len(bin(array_config[0])))

			# write the data to our state machine
			self.sm.write(array_config)


		def stop(self):
			self.sm.stop()


		def start(self):
			self.sm.restart()


# set up the array statemachines that handle the LED array
led_solid = array_sm((board.GP0, 3), pioc_solid)
led_flicker = array_sm((board.GP0, 3), pioc_flicker)

# integers that represent the binary data we need to send to the PIO program for each LED's pin configuration
# the binary representation corresponds to which pin is the positive lead for the LED
all_on = [3, 2, 1, 6, 4, 2, 5, 4, 1]
all_off = [3, 0, 0, 6, 0, 0, 5, 0, 0]

led_solid.write(all_on)
led_flicker.write([3, 0, 1, 6, 4, 0, 5, 0, 1])

# led_solid.stop()
led_flicker.stop()

while True:

	running = True

	if running:

		pass

