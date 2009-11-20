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

from OpenGL.GL import *
import numpy as N

class gl_shape:
	name = "nc"
	params = {}
	def get(self, amps, fft):
		x = 0
		fft /= len(fft)
		dx1 = 0
		current = self.data[self.age]
		while x < self.xlen:
			if x < 20:
				dx2 = dx1 + 2
				ratio = 1.0 + x / 8.0 
			elif x < 40:
				dx2 = dx1 + 10
				ratio = x / 4.0
			else:
				ratio = x / 2.0
				dx2 = dx1 + 64
			current[x] = N.max(fft[dx1:dx2]) * (ratio)
			dx1 = dx2
			x += 1
		return self
	def render(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		self.draw()

class wipeout(gl_shape):
	name = "wipeout"
	params = {}
	def __init__(self):
		self.age = 0
		self.data = N.zeros((25,50))
		self.xlen = len(self.data[0])
		self.zlen = len(self.data)
		self.xstep = 1 / (self.xlen/2.0)
		self.zstep = 1 / -5.0
		self.rotation_y = 0
		self.rotation_x = 0


	def draw(self):
		glTranslatef(-1., -1., -2.5)
		glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
		glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
		glBegin(GL_QUADS)
		z = 0
		while z < (self.zlen - 1):
			zoff = z+self.age
			a = self.data[(zoff)%(self.zlen)]
			b = self.data[(zoff+1)%(self.zlen)]
			z1 = z * self.zstep
			z2 = z1 + self.zstep
			x = 0
			while x < (self.xlen - 1):
				y1 = a[x]
				y2 = b[x]
				y3 = b[x+1]
				y4 = a[x+1]

				x1 = x * self.xstep 
				x2 = x1 + self.xstep

				color = (y1+y2+y3+y4)/4.0
				glColor3f(color, color * x1, 0.1)
				glVertex3f(x1, y1, z1)
				glVertex3f(x1, y2, z2)
				glVertex3f(x2, y3, z2)
				glVertex3f(x2, y4, z1)
				x += 1
			z += 1
		glEnd()

		self.age = (self.age - 1) % self.zlen

shapes = [wipeout()]

