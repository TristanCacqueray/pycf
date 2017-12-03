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

# ------------------------------------------------------------------------
# PyOpenGL Shader libs
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
        raise ValueError('Shader compilation failed')
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
# ------------------------------------------------------------------------


class wipeout:
    name = "wipeout"
    params = {
        "speed": shape_param(180, (0, 200), 1),
        "fscale": shape_param(60, (8, 400), 8),
        "yimp": shape_param(25, (1, 100), 1),
        "ximp": shape_param(50, (1, 100), 1),
    }

    def init_cam(self):
        # center/eye: camera start eye
        self.center =  [1.0, 1.4, -0.5]
        self.eye =  [1.2, 2.6, 4.0]

    def __init__(self):
        self.init_cam()

        # age: shape age
        self.age = 0
        # datas: fft storage for n and n-1
        self.datas = N.zeros((2,1000))
        # lists: fft opengl lists
        self.lists = N.zeros(300, dtype=int)
        # zlen: fft opengl lists len (== shape depth)
        self.zlen = len(self.lists)

        # shader: fft pixel shaders (contributed by wakko, thanks)
        self.shader = compile_program('''
    // Vertex program
    varying vec4 pos;
    varying vec3 normal, lightDir, eyeVec;

    void main() {
        normal = gl_NormalMatrix * gl_Normal;
        vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

        lightDir = vec3(gl_LightSource[0].position.xyz - vVertex);
        eyeVec = -vVertex;
        gl_Position = ftransform();
        pos = gl_Vertex;
    }
    ''', '''
    // Fragment program
    varying vec4 pos;
    varying vec3 normal, lightDir, eyeVec;
    const float cos_outer_cone_angle = 0.8; // 36 degrees


    void main() {
        // Fog
        float perspective_far = 1000.0;
        float fog_cord = (gl_FragCoord.z / gl_FragCoord.w) / perspective_far;

        float fog_density = 2; //0.0005;

        float fog = fog_cord * fog_density;
        vec4 fog_color = vec4(0., 0., 0., 0.);

        // Fft color
        float intensity = pos.y / 2.0;
        vec4 frag_color = vec4(intensity, intensity * pos.x, 0.1, 0.0);

        // Fft + fog
        //gl_FragColor = mix(fog_color, frag_color, clamp(1.0-fog, 0.0, 1.0));

        // Lightning spot
        vec4 amb =  frag_color * vec4(0.8, 0.8, 0.8, 1.0);
        vec4 spec = /* frag_color */ vec4(0.0, 0.0, 0.0, 1.0);
        vec4 diffuse = frag_color * 1.5; // vec4(0.9, 0.9, 0.9, 1.0);
        float shininess = 60.0;

        vec4 final_color = (gl_FrontLightModelProduct.sceneColor * amb) +
            (gl_LightSource[0].ambient * amb);

        vec3 L = normalize(lightDir);

        vec3 D = normalize(gl_LightSource[0].spotDirection);

        float cos_cur_angle = dot(-L, D);

        float cos_inner_cone_angle = gl_LightSource[0].spotCosCutoff;

        float cos_inner_minus_outer_angle = cos_inner_cone_angle -
                                            cos_outer_cone_angle;

        float spot = 0.0;
        spot = clamp((cos_cur_angle - cos_outer_cone_angle) /
            cos_inner_minus_outer_angle, 0.0, 1.0);


        vec3 N = normalize(normal);

        float lambertTerm = max( dot(N,L), 0.0);

        if(lambertTerm > 0.0)
        {
            final_color += gl_LightSource[0].diffuse *
                diffuse *
                lambertTerm * spot;

            vec3 E = normalize(eyeVec);
            vec3 R = reflect(-L, N);

            float specular = pow( max(dot(R, E), 0.0),
            shininess );

            final_color += gl_LightSource[0].specular *
            spec *
            specular * spot;
        }

        gl_FragColor = final_color;
    }
    ''')

        # boxs: shape border opengl list
        self.boxs = glGenLists(1)

        # Create glLists
        for i in range(self.zlen):
            self.lists[i] = glGenLists(1)


        # Shape OpenGL init
        glEnable(GL_COLOR_MATERIAL)
        glLoadIdentity()
#         glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 0.5))
#         glLightfv(GL_LIGHT0, GL_DIFFUSE, (0, 0, 0, 0.5))
#         glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 0, 1, 1))
#         glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 2.0)
#         glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 1.0)
#         glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.5)


        # shape border drawing
        xmax = 1.96
        glNewList(self.boxs, GL_COMPILE)
        glUseProgram(0)
        glBegin(GL_QUADS)
        glColor3f(0.2, 0.2, 0.2)
        glVertex3f(0, -4, 0)
        glVertex3f(0, 4, 0)
        glVertex3f(0, 4, -1000)
        glVertex3f(0, -4, -1000)

        glVertex3f(xmax, -4, 0)
        glVertex3f(xmax, 4, 0)
        glVertex3f(xmax, 4, -1000)
        glVertex3f(2, -4, -1000)

#         glColor3f(0.2, 0.1, 0.1)
#         glVertex3f(0, 4, 0)
#         glVertex3f(0, 4, -1000)
#         glVertex3f(xmax, 4, -1000)
#         glVertex3f(xmax, 4, 0)

#         glVertex3f(0, 0, 0)
#         glVertex3f(0, 0, -1000)
#         glVertex3f(xmax, 0, -1000)
#         glVertex3f(xmax, 0, 0)
        glEnd()
        glEndList()


    # render an fft step
    def render_fft(self, amps, fft):
        # get controller param
        ximp = self.params["ximp"].value / 100.0 #ximp: create impulsion on X axis
        yimp = self.params["yimp"].value / 100.0 #yimp: create impulsion on Y axis
        fscale = self.params["fscale"].value   #fscale: fft frequence cutoff
        self.speed = 20.1 - self.params["speed"].value / 10.0 # speed: ffts interval

        ## ----------------------------------- input fft conversion
        #t0 : current fft
        t0 = self.datas[self.age % 2]
        #t1 : previous fft
        t1 = self.datas[(self.age + 1) % 2]

        # convert input fft to scaled fft in t0
        for x in range(fscale):
            y0 = fft[x] * 8.0
            # if previous fft is higher, then we quantize the gap
            if t1[x] > y0:
                y0 = t1[x] - (t1[x] - y0) * yimp
            t0[x] = y0

        # create X impulsion
        for x in range(1, fscale):
            # if previous frequency is higher, then we quantize the gap
            if t0[x] < t0[x-1]:
                t0[x] = t0[x - 1] - (t0[x-1] - t0[x]) * ximp

        ## ----------------------------------- fft drawing
        # xstep: GL x step between freqs
        xstep = 1 / (fscale / 2.0)
        # zstep: GL z depth between ffts
        zstep = -1 / self.speed

        glNewList(self.lists[self.age], GL_COMPILE)
        glUseProgram(self.shader)
        glBegin(GL_QUADS)

#         p2              p1: (x1, t0[x], 0)
#        / \              p2: (x1, t1[x], zstep)
#      p1 /   \p3__________         p3: (x2, t1[x+1], zstep)
#         \   /   /   /   /         p4: (x2, t0[x], 0)
#        \ /___/___/___/
#         p4
        for x in range(fscale - 2):
            # quad x coords
            x1 = x * xstep
            x2 = x1 + xstep

            glVertex3f(x1, t0[x], 0)
            glVertex3f(x1, t1[x], zstep)
            glVertex3f(x2, t1[x+1], zstep)
            glVertex3f(x2, t0[x+1], 0)
        glEnd()
        glEndList()
        return self

    # render the whole shape
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        lpos =  [1.0, 4.0, 0.0]
        ldir =  [0.0, -4.0, -5.0]
        glLightfv(GL_LIGHT0, GL_POSITION, lpos)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, ldir)
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30)


        ## ----------------------------------- GL cam
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity();
        gluPerspective(45, 1, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity();


        gluLookAt(self.eye[0], self.eye[1], self.eye[2],
            self.center[0], self.center[1], self.center[2],
            0, 1, 0)


#         glCallList(self.boxs)

        ## ----------------------------------- FFTs drawing
        # zstep: GL z depth between ffts
        zstep = -1/self.speed
        for z in range(self.zlen):
            l = self.lists[(z+self.age)%self.zlen]
            if l:
                glCallList(l)
            glTranslatef(0., 0., zstep)
        self.age = (self.age - 1) % self.zlen

shapes = [wipeout()]
shapes[0].get = shapes[0].render_fft
