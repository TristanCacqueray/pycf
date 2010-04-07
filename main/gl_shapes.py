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
		"speed": shape_param(180, (0, 200), 1),
		"fscale": shape_param(60, (8, 400), 8),
		"yimp": shape_param(25, (1, 100), 1),
		"ximp": shape_param(50, (1, 100), 1),
	}
	def __init__(self):
		self.age = 0
		self.datas = N.zeros((2,1000))
		self.lists = N.zeros(1000, dtype=int)
		self.zlen = len(self.lists)
		self.boxs = glGenLists(1)
		for i in xrange(self.zlen):
			self.lists[i] = glGenLists(1)
		self.rotation = [0., 0., 0.]
		self.position = [0., 0., 0.]

		glEnable(GL_COLOR_MATERIAL)
		glLoadIdentity()
		#glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 0.5))
	        #glLightfv(GL_LIGHT0, GL_DIFFUSE, (0, 0, 0, 0.5))
	        #glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 0, 1, 1))
#		glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 2.0)
#		glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 1.0)
#		glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.5)

	
		xmax = 1.96
		glNewList(self.boxs, GL_COMPILE)
		glBegin(GL_QUADS)
		glColor3f(0.1, 0.1, 0.1)
		glVertex3f(0, 0, 0)
		glVertex3f(0, 4, 0)
		glVertex3f(0, 4, -1000)
		glVertex3f(0, 0, -1000)

		glVertex3f(xmax, 0, 0)
		glVertex3f(xmax, 4, 0)
		glVertex3f(xmax, 4, -1000)
		glVertex3f(2, 0, -1000)

		glColor3f(0.2, 0.1, 0.1)
		glVertex3f(0, 4, 0)
		glVertex3f(0, 4, -1000)
		glVertex3f(xmax, 4, -1000)
		glVertex3f(xmax, 4, 0)

		glVertex3f(0, 0, 0)
		glVertex3f(0, 0, -1000)
		glVertex3f(xmax, 0, -1000)
		glVertex3f(xmax, 0, 0)

		glEnd()
		glEndList()


	def render(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glTranslatef(self.position[1]-1., -1., self.position[0]  -2.5)
		glRotatef(self.rotation[0]+18, 1.0, 0.0, 0.0)
		glRotatef(self.rotation[1]+14, 0.0, 1.0, 0.0)
#		glLightfv(GL_LIGHT0, GL_POSITION, (1, 3, -2))
		#glCallList(self.boxs)
		z = 0
		#zstep = -1/((200.2 - self.params["speed"].value)/10.0)
		zstep = -1/self.speed
		while z < self.zlen:
			l = self.lists[(z+self.age)%self.zlen]
			if l:
				glCallList(l)
			z += 1
			glTranslatef(0., 0., zstep)
		self.age = (self.age - 1) % self.zlen

	def get(self, amps, fft):
		ximp = self.params["ximp"].value / 100.0
		yimp = self.params["yimp"].value / 100.0
		ximp = self.params["ximp"].value / 100.0
		xlen = self.params["fscale"].value
		self.speed = 20.1 - self.params["speed"].value / 10.0
		ratio = len(fft) / float(xlen)
		t0 = self.datas[self.age % 2]
		t1 = self.datas[(self.age + 1) % 2]
		x = 0
		while x < xlen:
#			y0 = N.max(fft[x*ratio:(x+1)*ratio]) * (1.0 + 10 * (x/float(xlen)))
			y0 = fft[x]# * (1.0 + 10 * (x/float(xlen)))
			y0 = y0 * 4.0
			if t1[x] > y0:
				y0 = t1[x] - (t1[x] - y0) * yimp
			t0[x] = y0
			x += 1

		x = 1
		while x < xlen:
			if t0[x] < t0[x-1]:
				t0[x] = t0[x - 1] - (t0[x-1] - t0[x]) * ximp
			x += 1

		xstep = 1/(xlen/2.0)
		zstep = -1/self.speed
		glNewList(self.lists[self.age], GL_COMPILE)
		glBegin(GL_QUADS)
		x = 0
		while x < (xlen - 2):
			y1 = t0[x]
			y2 = t1[x]
			y3 = t1[x+1]
			y4 = t0[x+1]

			x1 = x * xstep
			x2 = x1 + xstep
			color = (y1+y2+y3+y4) / 4.0
			cfront = (y1+y4) / 2.0
			cback = (y2+y3) / 2.0
			glColor3f(cfront, cfront * x1, 0.1)
			glVertex3f(x1, y1, 0)
			glColor3f(cback, cback * x1, 0.1)
			glVertex3f(x1, y2, zstep)
			glColor3f(cback, cback * x1, 0.1)
			glVertex3f(x2, y3, zstep)
			glColor3f(cfront, cfront * x1, 0.1)
			glVertex3f(x2, y4, 0)
			x += 1
		glEnd()
		glEndList()
		return self

shapes = [wipeout()]
#shapes = []

