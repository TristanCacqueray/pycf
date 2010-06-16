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
from pygame.locals import *
import Tkinter as Tk
import pygame
import time
import numpy as N

LightAmb=(0.0, 0.0, 0.0, 1.0)
LightDif=(1.0, 1.0, 1.0, 1.0)
LightSpec=(1.0, 1.0, 1.0, 1.0)


class scene:
	def pygame_init(self):
		self.surface = pygame.display.set_mode(self.dim, OPENGL|DOUBLEBUF|HWSURFACE)

	def gl_init(self):
		glShadeModel(GL_FLAT)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
    		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
#		glLightfv(GL_LIGHT0, GL_POSITION, (.5, .5, .5))
	        glLightfv(GL_LIGHT0, GL_AMBIENT, LightAmb)
	        glLightfv(GL_LIGHT0, GL_DIFFUSE, LightDif)
	        glLightfv(GL_LIGHT0, GL_SPECULAR, LightSpec)
#	        glEnable(GL_LIGHT0)
#	        glEnable(GL_LIGHTING)
		glEnable(GL_COLOR_MATERIAL)
#		glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.9, 0.5, 0.5, 1.0))

		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))

		glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 60.0 )



#		glViewport(0, 0, self.dim[0], self.dim[1])
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity();

		gluPerspective(45, 1, 1, 1000)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity();

	def __init__(self, dim = (640, 480)):
		self.dim = dim
		self.pygame_init()
		self.gl_init()
		self.root = Tk.Tk()

		# travelling_* : tuple (vector index, movement distance)
		self.travelling_rot = None
		self.travelling_pos = None
		# age : travelling age
		self.age = 0

	
	def close(self):
		pygame.quit()

	def update_age(self, lim = 131):
		if self.age >= lim - 1:
			self.age += 5
		else:
			self.age = lim

	# Handle user input and render the shape
	def do(self, shape, output = None):
	        for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
		pressed = pygame.key.get_pressed()
		if pressed[K_UP]:
			shape.center[1] -= 0.2
		if pressed[K_DOWN]:
			shape.center[1] += 0.2
		if pressed[K_LEFT]:
			shape.eye[0] += 0.2
		if pressed[K_RIGHT]:
			shape.eye[0] -= 0.2
		if pressed[K_r]:
			shape.init_cam()
		if pressed[K_q]:
			shape.center[0] -= 0.2
		if pressed[K_d]:
			shape.center[0] += 0.2
		if pressed[K_z]:
			shape.eye[1] += 0.2
		if pressed[K_s]:
			shape.eye[1] -= 0.2
		if pressed[K_a]:
			shape.eye[2] -= 0.2
		if pressed[K_w]:
			shape.eye[2] += 0.2

		if self.travelling_rot and self.age > 0:
			shape.center[self.travelling_rot[0]] += self.travelling_rot[1] * (self.age / 131.)
			if self.age == 1:
				self.travelling_rot = None
		if self.travelling_pos and self.age > 0:
			shape.eye[self.travelling_pos[0]] += self.travelling_pos[1] * (self.age / 131.)
			if self.age == 1:
				self.travelling_pos = None
		self.age -= 1

		if pressed[K_p]:
			print "self.center = ", shape.center
			print "self.eye = ", shape.eye

		# Shape rendering
		shape.render()

		if output:
			pygame.image.save(self.surface, output)
		self.root.update()

	# display rendered buffer
	def show(self, img):
		pygame.display.flip()


window = scene()
