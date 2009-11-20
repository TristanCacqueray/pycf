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
from cf_shapes import shape_param

class wipeout:
	name = "wipeout"
	params = {
		"depth": shape_param(20.0, (1, 200), 1),
		"width": shape_param(60.0, (1, 443), 1),
	}
	def __init__(self):
		self.age = 0
		self.datas = N.zeros((2,1000))
		self.lists = N.zeros(1000, dtype=int)
		self.zlen = len(self.lists)
		for i in xrange(self.zlen):
			self.lists[i] = glGenLists(1)
		self.rotation = [0., 0., 0.]
		self.position = [0., 0., 0.]


	def render(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glTranslatef(self.position[1]-1., -1., self.position[0]  -2.5)
		glRotatef(self.rotation[0], 1.0, 0.0, 0.0)
		glRotatef(self.rotation[1], 0.0, 1.0, 0.0)
		z = 0
		zstep = -1/float(self.params["depth"].value)
		while z < self.zlen:
			l = self.lists[(z+self.age)%self.zlen]
			if l:
				glCallList(l)
			z += 1
			glTranslatef(0., 0., zstep)
		self.age = (self.age - 1) % self.zlen

	def get(self, amps, fft):
		x = 0
		xlen = self.params["width"].value
		xstep = 1/(xlen/2.0)
		ratio = len(fft) / float(xlen)
		t0 = self.datas[self.age % 2]
		t1 = self.datas[(self.age + 1) % 2]
		while x < xlen:
			y0 = N.max(fft[x*ratio:(x+1)*ratio]) * (1.0 + 10 * (x/float(xlen)))
			y0 = y0 * 4.0
			if t1[x] > y0:
				y0 = t1[x] - (t1[x] - y0) * 0.25
			t0[x] = y0
			x += 1

		glNewList(self.lists[self.age], GL_COMPILE)
		glBegin(GL_QUADS)
		x = 1
		zstep = -1/float(self.params["depth"].value)
		while x < (xlen - 1):
			y1 = t0[x]
			y2 = t1[x]
			y3 = t1[x+1]
			y4 = t0[x+1]

			x1 = x * xstep
			x2 = x1 + xstep
			color = (y1+y2+y3+y4) / 4.0
			glColor3f(color, color * x1, 0.1)
			glVertex3f(x1, y1, 0)
			glVertex3f(x1, y2, zstep)
			glVertex3f(x2, y3, zstep)
			glVertex3f(x2, y4, 0)
			x += 1
		glEnd()
		glEndList()
		return self

shapes = [wipeout()]
#shapes = []

