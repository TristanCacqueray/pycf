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
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
import Tkinter as Tk
import pygame
import time
import numpy as N

LightAmb=(0.7,0.7,0.7)
LightDif=(1.0,1.0,0.0)
LightPos=(4.0,4.0,6.0,1.0)


class scene:
	def pygame_init(self):
		pygame.init()
		self.surface = pygame.display.set_mode(self.dim, OPENGL|DOUBLEBUF|HWSURFACE)
	
	def show(self, img):
		pygame.display.flip()


	def gl_init(self):
		glutInit([])
		glClearColor(0.0, 0.0, 0.0, 0.0)
		#glShadeModel(GL_SMOOTH)
		#glClearDepth(1.0)
	
		#glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
    		#glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

		#glViewport(0, 0, self.dim[0], self.dim[1])

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(60, 1, 0.1, 100)
		glMatrixMode(GL_MODELVIEW)



	def __init__(self, dim = (800, 600)):
		self.dim = dim
		self.pygame_init()
		self.gl_init()
	
	def close(self):
		pygame.quit()

	def do(self, shape, output = None):
	        for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
		pressed = pygame.key.get_pressed()
		#step = 0.1
		step = 0.05
#		if pressed[K_q]:			shape.rotation[0] += step
#		if pressed[K_d]:			shape.rotation[0] -= step
#		if pressed[K_z]:			shape.position[1] -= step	# high
#		if pressed[K_s]:			shape.position[1] += step
#		if pressed[K_LEFT]:			shape.position[0] += step	# width
#		if pressed[K_RIGHT]:			shape.position[0] -= step
#		if pressed[K_UP]:			shape.position[2] += step	# depth
#		if pressed[K_DOWN]:			shape.position[2] -= step
#		if pressed[K_p]:			print "position:", shape.position, "\trotation:", shape.rotation
		if pressed[K_r]:			cam.reset()
		if pressed[K_UP]:			cam.avance(0.01)
		if pressed[K_DOWN]:			cam.avance(-0.01)
		if pressed[K_LEFT]:			cam.tourne(-0.1)
		if pressed[K_RIGHT]:			cam.tourne(0.1)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		cam.apply()

		shape.render()

		if output:
			pygame.image.save(self.surface, output)
		#self.root.update()

sin = N.zeros(361)
cos = N.zeros(361)
for i in xrange(361):
	sin[i] = N.sin(i/360.0*6.283185)
	cos[i] = N.cos(i/360.0*6.283185)

class camera:
	x = 0
	z = 0
	a = 0
	def reset(self):
		self.x, self.z, self.a = 0, 0, 0
	def avance(self, step):
		self.x += step * sin[self.a]
		self.z -= step * cos[self.a]
	def tourne(self, ang):
		self.a += ang
		self.a = self.a % 360
	def apply(self):
		glRotatef(self.a, 0.0, 1.0, 0.0)
		glTranslatef(-self.x, 0, -self.z)
	
cam = camera()
	

black = (0., 0., 0., 1.)
sun = (1., 1., 0.9, 1.)
white = (1., 1., 1., 1.)

def water_synth(width, heigh):
	#for i in xrange(num_chunks):
	#	chunks.append(N.random.poisson(50, (width * heigh / num_chunks)))
	#chunks = N.concatenate(chunks)
	pixlen = width * heigh
#	chunks = N.random.poisson(60, size=pixlen)
#	chunks = N.random.uniform(0, 50, size=pixlen)
	chunks = N.random.logseries(0.9, size=pixlen) * 2
	for y in xrange(heigh):
		for x in xrange(width):
			val = int(chunks[x+y*heigh])
			v1 = val
			v2 = val
			v3 = val
#			if y+1 < heigh:
#				up = chunks[(x) + (y+1)*heigh]
#				if val - up < 0:
#					val = (up-val) / 2
			if y > 0:
				n = chunks[(x) + (y-1)*heigh]
				v1 = (val + n) / 2
#				if val > n:	v1 = n + 2
#				else:		val = n - 20
#			if x+1 < width:
#				right = chunks[(x+1) + (y)*heigh]
#				if val - right < 0:
#					val = (right-val)/2
			if x > 0:
				n = chunks[(x-1) + (y)*heigh]
				v2 = (val + n) / 2
				#if val > n:	v2 = n + 2
				#else:		val = n - 20

			if y > 0 and x > 0:
				n = chunks[(x-1) + (y - 1) * heigh]
				v3 = (val + n) / 2
				#if val > n:	v3 = n + 2

#			if y == 0 or x == 0:
#				val = 0

			chunks[x+y*heigh] = (val + v1 + v2 + v3) / 4
	pixmap = N.zeros(pixlen*4, dtype=N.uint8)
	for x in xrange(0, pixlen * 4, 4):
		pixmap[x] = 20 + chunks[x/4]   #R
		pixmap[x+1] = 23 + chunks[x/4] #G
		pixmap[x+2] = 206		#B
		pixmap[x+3] = 0			#A
	return pixmap

class Sphere:
	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
	def render(self):
		glPushMatrix()
		glTranslatef(self.pos[0], self.pos[1], self.pos[2])
		glutSolidSphere(self.size, 40, 40)
		glPopMatrix()

		

			
class shape:
	name = "test"
	def __init__(self):
		self.rotation = [0.] * 3
		self.position = [0.] * 3
		self.objs = [Sphere((0, 0.8, 0.8), 0.9), Sphere((1, 1.5, 0.8), 0.5), Sphere((-1, 1, 0.8), 0.2)]
		glLightfv(GL_LIGHT0, GL_AMBIENT, sun)#black)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, sun)
		glLightfv(GL_LIGHT0, GL_SPECULAR, sun)
#		glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.2,0.2,0.2,1.))
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		self.tex_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.tex_id)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

		width, heigh = 10, 10
		glTexImage2D(GL_TEXTURE_2D, 0, 4, width, heigh, 0, GL_RGBA, GL_UNSIGNED_BYTE, water_synth(width, heigh))
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#		glEnable(GL_COLOR_MATERIAL)
#		glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
#		glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, (1.,1.,1.,1.))
#		glMaterial(GL_FRONT_AND_BACK, GL_EMISSION, (0.,0.,0.,1.))

	def render(self):
#		glEnable(GL_LIGHTING)
		#glRotatef(self.rotation[0], 0, 1, 0)
#		gluLookAt(
#			self.position[0], self.position[1], self.position[2] + 3, 
			#self.position[0] + self.rotation[0], self.position[1], self.position[2],
#			0, 0, -1,
			#0, 0, -1,
#			1, 1, 1
#		)

#		glTranslatef(

#		glLoadIdentity()
#		glTranslatef(self.position[0], self.position[1], self.position[2] - 3)
		glDisable(GL_TEXTURE_2D)
		glTranslatef(0, 0, -3)
#		glColor3f(1, 1, 1)

		# light
		glLightfv(GL_LIGHT0, GL_POSITION, (-0.9, -0.9, 0))

		glPushMatrix()
		glTranslatef(-0.9, -0.9, 0)
		glutWireCube(0.1)
		glPopMatrix()


		for obj in self.objs:
			obj.render()

#		glPushMatrix()
#		glTranslatef(0, 0.8, 0.8)
#		glColor4f(1, 0, 1, 0)
#		glutSolidSphere(0.1, 40, 40)
#		glPopMatrix()
#		glColor4f(1, 1, 1, 1)
#		glutSolidSphere(1.0, 40, 40)

		#flour
		glEnable(GL_TEXTURE_2D)
		glBegin(GL_QUADS)
#		glMaterialfv(GL_FRONT, GL_AMBIENT, black)
#		glMaterialfv(GL_FRONT, GL_SPECULAR, black)
#		glMaterialfv(GL_FRONT, GL_EMISSION, black)
#		glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.1, 0.5, 0.8, 1.0))
#		glMaterialfv(GL_FRONT, GL_SHININESS, white)
		glTexCoord2i(0,0); glVertex3f(-4, -1.5, -4)
		glTexCoord2i(0,1); glVertex3f(-4, -1.5, 4)
		glTexCoord2i(1,1); glVertex3f(4, -1.5, 4)
		glTexCoord2i(1,0); glVertex3f(4, -1.5, -4)
		glEnd()



window = scene()
s = shape()
while True:
	window.do(s)
	window.show(None)
del s
