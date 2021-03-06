import subprocess
from subprocess import PIPE
import threading
import time

class Volume:

	def __init__(self, sb):
		self.sb = sb

	def init(self):
		# We specify that we started
		self.running = True
		# We get the current level
		command = ["pulseaudio-ctl", "full-status"]
		a = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
		(cout, cerr) = a.communicate()
		self.curr_volume = int(cout.decode("ascii").split(" ")[0])
		# We set the slider at the proper position
		curr_position = min(float(self.curr_volume) / 100.0, 1.0)
		self.sb.setPosition(curr_position) # We set the slider position according to the current volume (but not more than 100%)

		# We wait for the slider to be at the righ position
		while abs(self.sb.getPosition() - curr_position) > 0.01:
			time.sleep(1. / 60.)

		self.periodic_thread = threading.Thread(target = self.update)
		self.periodic_thread.start()

	def stop(self):
		self.running = False

	def keydown(self, event):
		return

	def keyup(self, event):
		return

	def update(self):
		while True:
			if not self.running:
				return
			# We check if the position of the slider changed:
			new_position = self.sb.getPosition()
			new_volume = new_position * 100.0
			# If the change is greater than 1%, then we update the volume
			# (We do that check as the position given by the slidebar changes slightly from time to time)
			if abs(new_volume - self.curr_volume) > 1:
				command = ["pulseaudio-ctl", "set", str(int(new_volume))]
				a = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
				(cout, cerr) = a.communicate()
				self.curr_volume = new_volume
			# We repeat this process at a 60Hz frequency
			time.sleep(1. / 60.)

