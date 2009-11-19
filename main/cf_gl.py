from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import pygame
import time
import numpy as N

class scene:
	def pygame_init(self):
		pygame.init()
		self.surface = pygame.display.set_mode(self.dim, OPENGL|DOUBLEBUF|HWSURFACE)

	def gl_init(self):
		glShadeModel(GL_FLAT)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
	
		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LEQUAL)
    		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

		glViewport(0, 0, self.dim[0], self.dim[1])
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45, 1, 1, 1000)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def __init__(self, dim = (640, 480)):
		self.dim = dim
		self.pygame_init()
		self.gl_init()

		self.age = 0
		self.rotation_y = 0.0
		self.rotation_x = 20.0

		self.data = N.zeros((30,50))

		self.xlen = len(self.data[0])
		self.zlen = len(self.data)
		self.xstep = 1 / (self.xlen/2.0)
		self.zstep = 1 / -5.0
	
	def close(self):
		pygame.quit()

	def do(self, fft, output = None):
	        for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
		pressed = pygame.key.get_pressed()
		if pressed[K_LEFT]:
			self.rotation_y += 1
		if pressed[K_RIGHT]:
			self.rotation_y -= 1
		if pressed[K_UP]:
			self.rotation_x += 1
		if pressed[K_DOWN]:
			self.rotation_x -= 1
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

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()

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
		pygame.display.flip()

		self.age = (self.age - 1) % self.zlen
		if output:
			pygame.image.save(self.surface, output)
