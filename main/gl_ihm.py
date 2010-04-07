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
		glShadeModel(GL_FLAT)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
	
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
    		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
#		glEnable(GL_LIGHTING)
#		glEnable(GL_LIGHT0)

#		glLightfv(GL_LIGHT0, GL_POSITION, (.5, .5, .5))
#	        glLightfv(GL_LIGHT0, GL_DIFFUSE, LightDif)
#	        glLightfv(GL_LIGHT0, GL_POSITION, LightPos)
#	        glEnable(GL_LIGHT0)
#	        glEnable(GL_LIGHTING)
#		glEnable(GL_COLOR_MATERIAL)
#		glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )



		glViewport(0, 0, self.dim[0], self.dim[1])
		glMatrixMode(GL_PROJECTION)
		gluPerspective(45, 1, 1, 1000)
		glMatrixMode(GL_MODELVIEW)

	def __init__(self, dim = (800, 600)):
		self.dim = dim
		self.pygame_init()
		self.gl_init()
		self.root = Tk.Tk()
	
	def close(self):
		pygame.quit()

	def do(self, shape, output = None):
	        for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
		pressed = pygame.key.get_pressed()
		if pressed[K_r]:
			shape.position = [0]*3
			shape.rotation = [0]*3
		if pressed[K_q]:
			shape.position[1] += 0.1
		if pressed[K_d]:
			shape.position[1] -= 0.1
		if pressed[K_z]:
			shape.position[0] += 0.1
		if pressed[K_s]:
			shape.position[0] -= 0.1
		if pressed[K_LEFT]:
			shape.rotation[1] += 0.5
		if pressed[K_RIGHT]:
			shape.rotation[1] -= 0.5
		if pressed[K_UP]:
			shape.rotation[0] += 0.5
		if pressed[K_DOWN]:
			shape.rotation[0] -= 0.5
		if pressed[K_p]:
			print "rotation:", shape.rotation
			print "position:", shape.position
		shape.render()

		if output:
			pygame.image.save(self.surface, output)
		self.root.update()

window = scene()
