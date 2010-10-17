# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import random
from math import *
import numpy as N
ALL, LOW, MED, HIGH = range(4)

global gl_cpt

class shape_param:
	def __init__(self, value, range = (0, 127), resolution = 1):
		self.value = value
		self.range = range
		self.resolution = resolution
class shape:
	name = "nc"
	params = {}
	size = 123
	background_color = "b -1"
	amps = [0] * 4
	def __init__(self):
		self.shape = [
			"startshape %s" % self.name,
			"background { %s }" % self.background_color,
			"size { s %d }" % self.size,
			"rule %s {" % self.name
		]
		self.age = 0
	def get(self, amps, fft):
		del self.shape[4:]

		for idx in xrange(len(amps)):
			self.amps[idx] = int(amps[idx] * 100) / 100.0
		self.fft = fft

		self.process()
		self.shape.append("}")
		self.age  += 1
		return "\n".join(self.shape)

# SHAPES
red = "h 10 sat 0.9 b 1"
green = "sat 0.9 hue 96 b 1"
class spirals(shape):
	name = "spirals"
	params = {
		"spikes": shape_param(3, (0,15), 1),
		"xcurve": shape_param(1, (0, 4), 0.1),
		"ycurve": shape_param(2, (0, 4), 0.1),
		"circles": shape_param(3, (0,20), 1),
		"circle_len": shape_param(15, (0, 30), 1)
	}
	state = {
		"bg_hue": 230,
		"spike_curve": 1,
		"spiral_rotation": 0, "spiral_accel": 0,
		"spiral_rotation_accel": 0, "spike_rotation": 1, 
		"circle_accel": 0, "circle_rotation": 0
	}
	def gen_spirals(self):
		cur_curve = self.state["spike_curve"]
		new_curve = 1 + 10 * self.amps[LOW]
		if new_curve < cur_curve:
			if cur_curve - new_curve > 0.5:
				new_curve = cur_curve - 0.5
		elif new_curve - cur_curve < 0.08:	new_curve = cur_curve
		self.state["spike_curve"] = new_curve

		cur_rot = self.state["spiral_rotation"]
		cur_accel = self.state["spiral_accel"]
		new_accel = self.amps[MED] / 2
		if new_accel < cur_accel:	new_accel = cur_accel - 0.005
		cur_rot = cur_rot - new_accel
		self.state["spiral_accel"] = new_accel
		self.state["spiral_rotation"] = cur_rot

		if not self.params["spikes"].value:
			return
		xstep = self.params["xcurve"].value
		ystep = self.params["ycurve"].value
		ang_step = 2*pi/self.params["spikes"].value
		color = red
		for i in xrange(int(self.params["spikes"].value)):
			self.shape.append(
				"100 * {y %.3f x %.3f rotate %.3f size 0.98 h 0.5 z 1} CIRCLE {h 10 sat 0.9 b 1 s 3}" % (
					ystep * sin(cur_rot + i * ang_step),
					xstep * cos(cur_rot + i * ang_step),
					new_curve
				)
			)
	def gen_circles(self):
		cur_rot = self.state["circle_rotation"]
		cur_accel = self.state["circle_accel"]
		new_accel = self.amps[HIGH] / 5.0
		if new_accel < cur_accel:	new_accel = cur_accel - 0.005
		cur_rot = cur_rot + new_accel + 0.01
		self.state["circle_accel"] = new_accel
		self.state["circle_rotation"] = cur_rot

		if not self.params["circles"].value:
			return
		clen = self.params["circle_len"].value
		ang_step = 2*pi/self.params["circles"].value
		for idx in xrange(int(self.params["circles"].value)):
			i = 40 + 2.5 * idx
			this_rot = cur_rot + idx * ang_step
			if idx & 1:
				this_rot = -1 * this_rot
			self.shape.append(
				"%d * {y 1 r 15 h 8 } TRIANGLE {y %f x %f s 2 sat 1 b 1 h 60}" % (
					clen,
					i * sin(this_rot),
					i * cos(this_rot)
				)
			)

					
	def set_state(self, elem, value, down_step = None, up_step = None):
		prev = self.state[elem]
		if down_step and value < prev:
			value = prev - down_step
		elif up_step and value > prev:
			value = prev + up_step
		self.state[elem] = value	
	def process(self):
		cur_bg = self.state["bg_hue"]
		new_bg = 180 + 50 * self.amps[ALL]
		if new_bg < cur_bg:		new_bg = cur_bg - 0.5
		elif new_bg - cur_bg < 5:	new_bg = cur_bg
		self.state["bg_hue"] = new_bg
		self.shape[1] = "background { h %.3f sat 0.8 b %.3f}" % (new_bg, -0.5 + abs(230 - new_bg)/230.0)

		self.gen_spirals()
		self.gen_circles()

class twist(shape):
	name = "TWISTA"
	size = 80
	background = "b -.89"
	idx = 0
	def process(self):
		main_rot = 100 - (self.amps[1] * 100)
		spi_rot = 10 - (self.amps[2] * 100)
		if self.idx % 20 == 0:
			print main_rot, spi_rot
		self.idx += 1
		self.shape += ["TWIST {}",
			"TWISTA  {r %.5f s .9 hue -3 b .15}" % main_rot,
			"TWISTA {y 23 r -23 s .3 hue 19 b .15}",
			"TWISTA {y -23 r -23 s .3 hue -13 b .15}",
			"}"
			"rule TWIST {",
			"TWIT {s 5}",
			"TWIT {s 4.5 r 45}",
			"}"
			"rule TWIT {",
			"BALL {}",
			"BALL {y 1}",
			"BALL {y -1}",
			"BALL {y 2}",
			"BALL {y -2}",
			"BALL {y 3}",
			"BALL {y -3}",
			"TWIT {r %.5f s .92}" % spi_rot,
			"}"
			"rule BALL {",
			"CIRCLE {s .95 hue 160 saturation .75 b .2}",
		]

class twofirs(shape):
	name = "twofirs"
	params = {
		"spikes": shape_param(1, (0,30), 1),
		"size": shape_param(3, (0,200), 1),
		"num": shape_param(50, (10, 200), 1),
	}
	size = 500
	last_low = 0
	last_high = 0
	last_mid = 0
	steps = range(0, 300, 10)
	def process(self):
		self.shape[2] = ""
		a, alow, amid, ahigh = self.amps
		if alow < self.last_low:	alow = self.last_low - 0.02
		if amid < self.last_mid:	amid = self.last_mid - 0.02
		if ahigh < self.last_high:	ahigh = self.last_high - 0.01
		self.last_low, self.last_mid, self.last_high = alow, amid, ahigh
		size = self.params["size"].value
		num = self.params["num"].value
		for idx in xrange(self.params["spikes"].value):
			step = exp(idx / 5.0) #self.steps[idx/2]
			side = 1
			if idx & 1:
				side = -1

			for x,r,y,h in ((ahigh, alow, 1, 60), (-alow, ahigh, -1, 219)):
				x = 2 * x * side * step
				r = 10 * r + step / 2.0 * y
				y *= side
				self.shape.append(
					"%d * { x %.3f y %.3f r %.3f z 1 s 0.99 h -0.4 } TRIANGLE { hue %d b %f sat 1 s %.3f }" % (
					num, x, y, r, h, 0.5+amid, size * (1 - idx / 30.0))
				)
			

#import Gnuplot
class drops(shape):
	name = "drops"
	colors = ( "h 60 b 0.9 sat %f", "h 220 b 0.9 sat %f", "h 28 b 0.9 sat %f" )
	drops = []
	params = {
		"scale": shape_param(1, (1,20), 0.1),
		"limit": shape_param(0.15, (0,1), 0.01),
	}
	limit = 5
	last_freqs = N.zeros(1024) - limit
	#g = Gnuplot.Gnuplot()
	class drop:
		def __init__(self, pos, color, size, shape, vec):
			self.pos, self.color, self.size, self.shape, self.age = pos, color, size, shape, 1
			self.vec = vec

	def gen_shapes(self, amp):
		idx = 0
		sat = 0.2 + amp*1.5
		while idx < len(self.drops):
			drop = self.drops[idx]
			self.shape.append("%d * { %s } %s { %s %s a 0.9 s %.3f }" % (
				drop.age,
				drop.vec,
				drop.shape,
				drop.pos,
				drop.color,# % sat,
				drop.size,
			))
			drop.age += 2
			drop.size -= 0.8
			if drop.size < 0.2:
				del self.drops[idx]
			else:
				idx += 1
	def process(self):
		self.fft /= 100
#		self.g('set yrange [0:2]')
#		self.g.plot(self.fft)

		#print len(self.fft), N.max(self.fft)
		freqs = len(self.fft) / self.params["scale"].value
		limit = self.params["limit"].value
		self.fft *= 1000.0
		for i in xrange(int(freqs)):
			if self.fft[i] > (limit#-i/float(freqs)*0.4
				):# and self.age - self.last_freqs[i] > self.limit:
				pos = random.gauss(0, 20)
				if pos > 0:
					pos = min(pos, 60)
					vec = "y 3 r %.3f z -1 a -0.4" % (pos / 60.0 * -10)
				else:
					pos = max(pos, -60)
					vec = "y 3 r %.3f z -1 a -0.4" % (pos / 60.0 * -10)
				self.drops.append(
					drops.drop(
					"y %.3f x %.3f r 0" % (-60 + i/float(freqs) * 120, pos),#*120-60),
					"h %d b 1 sat 1" % (30 - (i/float(freqs) * 30) - (abs(pos)/60.0 * 30) ),
					2 + 1 * self.fft[i],# * (1+i/float(freqs) * 2) ,
					"CIRCLE", vec)
				)
				self.last_freqs[i] = self.age
		if len(self.drops) > 1024:
			print "%d drops !" % len(self.drops)
		
		self.gen_shapes(self.amps[ALL])

shapes = [twofirs(), spirals(), drops(), twist()]
