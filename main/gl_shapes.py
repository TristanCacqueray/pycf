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

from ctypes import *
import sys
 
import pygame
from pygame.locals import *
 
try:
    # For OpenGL-ctypes
    from OpenGL import platform
    gl = platform.OpenGL
except ImportError:
    try:
        # For PyOpenGL
        gl = cdll.LoadLibrary('libGL.so')
    except OSError:
        # Load for Mac
        from ctypes.util import find_library
        # finds the absolute path to the framework
        path = find_library('OpenGL')
        gl = cdll.LoadLibrary(path)
 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
 
glCreateShader = gl.glCreateShader
glShaderSource = gl.glShaderSource
glShaderSource.argtypes = [c_int, c_int, POINTER(c_char_p), POINTER(c_int)]
glCompileShader = gl.glCompileShader
glGetShaderiv = gl.glGetShaderiv
glGetShaderiv.argtypes = [c_int, c_int, POINTER(c_int)]
glGetShaderInfoLog = gl.glGetShaderInfoLog
glGetShaderInfoLog.argtypes = [c_int, c_int, POINTER(c_int), c_char_p]
glDeleteShader = gl.glDeleteShader
glCreateProgram = gl.glCreateProgram
glAttachShader = gl.glAttachShader
glLinkProgram = gl.glLinkProgram
glGetError = gl.glGetError
glUseProgram = gl.glUseProgram
 
GL_FRAGMENT_SHADER = 0x8B30
GL_VERTEX_SHADER = 0x8B31
GL_COMPILE_STATUS = 0x8B81
GL_LINK_STATUS = 0x8B82
GL_INFO_LOG_LENGTH = 0x8B84
 
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    source = c_char_p(source)
    length = c_int(-1)
    glShaderSource(shader, 1, byref(source), byref(length))
    glCompileShader(shader)
    
    status = c_int()
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
    if not status.value:
        print_log(shader)
        glDeleteShader(shader)
        raise ValueError, 'Shader compilation failed'
    return shader
 
def compile_program(vertex_source, fragment_source):
    vertex_shader = None
    fragment_shader = None
    program = glCreateProgram()
 
    if vertex_source:
        vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
        glAttachShader(program, vertex_shader)
    if fragment_source:
        fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
        glAttachShader(program, fragment_shader)
 
    glLinkProgram(program)
 
    if vertex_shader:
        glDeleteShader(vertex_shader)
    if fragment_shader:
        glDeleteShader(fragment_shader)
 
    return program
 
def print_log(shader):
    length = c_int()
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(length))
 
    if length.value > 0:
        log = create_string_buffer(length.value)
        glGetShaderInfoLog(shader, length, byref(length), log)
        print >> sys.stderr, log.value

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
		self.lists = N.zeros(150, dtype=int)
		self.zlen = len(self.lists)
		self.boxs = glGenLists(1)
		self.shader = compile_program('''
	// Vertex program
	varying vec4 pos;

	void main() {
		gl_Position = ftransform();
		pos = gl_Vertex;
	}
	''', '''
	// Fragment program
	varying vec4 pos;

	void main() {
		gl_FragColor.rgb = vec3(0.8, pos.y, pos.x);
	}
	''')

		for i in xrange(self.zlen):
			self.lists[i] = glGenLists(1)
		self.rotation = [0., 0., 0.]
		self.position = [0., 0., 10.]
		self.rotation = [8.0, -33.5, 0.0]
#		self.rotation =  [8.0, 1., 0.0]
		self.position = [-1.8000000000000005, 0.20000000000000004, 0.0]
#		self.position = [-1.8000000000000005, -0.20000000000000004, 0.0]



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
		glFogi(GL_FOG_COORD_SRC, GL_FRAGMENT_DEPTH);

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity();

                gluPerspective(45, 1, 1, 1000)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity();

#		gluLookAt(-10, 10, -50, 0, 0, 10, 0, 1, 0)
		glTranslatef(self.position[1]-1., -1., self.position[0]  -2.5)
		glRotatef(self.rotation[0]+18, 1.0, 0.0, 0.0)
		glRotatef(self.rotation[1]+14, 0.0, 1.0, 0.0)
		#glLightfv(GL_LIGHT0, GL_POSITION, (1, 3, -2))
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
		fft = fft * 2
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
		#glUseProgram(self.shader)
		glBegin(GL_QUADS)
		x = 0
		# draw a frame
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

