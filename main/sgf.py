#!/usr/bin/python

import re
import time

class World:
    def __init__(self, size):
        self.size = size
        self.world = [None] * (size**2)

    def walk(self, coord):
        for x,y in [
            (-1, 0),
            (0, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]:
            if coord[0] + x < self.size and coord[0] + x >= 0 and \
               coord[1] + y < self.size and coord[1] + y >= 0:
                yield (coord[0]+x, coord[1]+y)

    def is_dead(self, color, coord):
        if coord[0] >= self.size or coord[1] >= self.size:
            return True

        if self.get(coord) == None:
            return False

    def set(self, color, coord):
        pos = coord[0] + coord[1] * self.size
        #if self.world[pos] != None:
        #     raise RuntimeError("[%s:%s]: Wrong move!" % (color, coord))
        self.world[pos] = color
        dead_stones = []
        return dead_stones

    def get(self, coord):
        return self.world[coord[0] + coord[1] * self.size]

    def __str__(self):
        s = ""
        for y in range(self.size):
            for x in range(self.size):
                i = self.world[y * self.size + x]
                if i == None:
                    s += "."
                elif i == True:
                    s += "W"
                else:
                    s += "B"
            s += "\n"
        return s


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as N

from cf_shapes import shape_param

class Sgf:
    def __init__(self, fname):
        self.moves = []
        self.timeline = {}
        self.size = 0
        self.load_file(fname)
        self.render()
        print(self.timeline)

    def render(self):
        world = World(self.size)
        pos = 0
        for color, coord in self.moves:
            events = []
            if coord[0] == self.size and coord[1] == self.size:
                events.append(('p', color))
            else:
            #     print "======", color, coord
                events.append(('s', color, coord))
                for dead_stone in world.set(color, coord):
                    events.append(('r', dead_stone))
            #     print world
            self.timeline[pos] = events
            pos += 1

    def load_file(self, fname):
        #player_clocks = []
        for line in open(fname).readlines():
            pos = 0
            while True:
                m = re.search(r"([A-Z]+)\[([^\]]*)\]", line[pos:])
                if not m:
                    break
                pos += len(m.group()) + m.start()
                move = m.groups()
                if move[0] == 'SZ':
                    self.size = int(move[1])
#                 elif move[0] == 'TM':
#                     self.time = 1800 # decode time here, default to 30minutes
#                     players_clocks = [self.time] * 2
#                 elif move[0] in ('WL', 'BL'):
#                     if move[0] == 'WL':
#                         clock = 0
#                     else:
#                         clock = 1
#                     delta = players_clocks[clock] - int(move[1])
#                     players_clocks[clock] = int(move[1])
#                     self.moves[-1].append(delta)
                elif move[0] in ('W', 'B'):
                    if move[0] == 'W':
                        color = True
                    else:
                        color = False
                    coord = (
                        ord(move[1][0]) - ord('a'),
                        self.size - 1 - (ord(move[1][1]) - ord('a'))
                    )
                    self.moves.append([color, coord])

import math
class Stones:
    def __init__(self, size, color, pos):
        self.age = 0
        self.size = size
        if color:
            self.color = (0.9, 0.9, 0.9)
        else:
            self.color = (0.25, 0.25, 1.0)
        self.pos = pos

    def render(self):
        self.age += 1
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        age = math.log(self.age / 2.0) / 8.0
        glColor3f(self.color[0] - age, self.color[1] - age, self.color[2] - age)
        glutSolidSphere(self.size, 20, 20)
        glPopMatrix()



class SgfGl:
    def init_cam(self):
        # center/eye: camera start eye
        self.center =  [0.0, 0.0, 0.0]
        self.eye =  [1., 1.0, 4.0]
    def __init__(self, sgf):
        self.init_cam()
        glutInit([])
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        self.age = None
        self.pos = 0
        self.sgf = sgf
        self.grid = glGenLists(1)
        self.stones = {}
        self.render_grid()

    def render_grid(self):
        glNewList(self.grid, GL_COMPILE)
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.1, 0.1)
        self.step = 1.0 / self.sgf.size
        size = 1.0 - self.step
        for x in range(self.sgf.size):
            xpos = x * self.step
            glVertex3f(xpos, 0, 0)
            glVertex3f(xpos, size, 0)
            glVertex3f(xpos + 0.01, size, 0)
            glVertex3f(xpos + 0.01, 0, 0)
        for y in range(self.sgf.size):
            ypos = y * self.step
            glVertex3f(0, ypos, 0)
            glVertex3f(size, ypos, 0)
            glVertex3f(size, ypos + 0.01, 0)
            glVertex3f(0, ypos + 0.01, 0)
        glEnd()
        glEndList()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glLoadIdentity()
        #glTranslatef(self.position[1]-0.5, -0.5, self.position[0]  -2.5)
        #glRotatef(self.rotation[0]+18, 1.0, 0.0, 0.0)
        #glRotatef(self.rotation[1]+14, 0.0, 1.0, 0.0)


        ## ----------------------------------- GL cam
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity();
        gluPerspective(45, 1, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity();


        gluLookAt(self.eye[0], self.eye[1], self.eye[2],
            self.center[0], self.center[1], self.center[2],
            0, 1, 0)


        glCallList(self.grid)

        if not self.age or time.time() - self.age > 0.05:
            self.age = time.time()
            self.pos += 1
            if self.pos in self.sgf.timeline:
                for ev in self.sgf.timeline[self.pos]:
                    if ev[0] != 's':
                        continue
                    self.stones[ev[2]] = Stones(self.step / 2.0,
                        ev[1], (
                        ev[2][0] * self.step,
                        ev[2][1] * self.step
                    ))

        for stone in self.stones.values():
            stone.render()


def play(s):
    import gl_ihm
    sgl = SgfGl(s)
    w = gl_ihm.window
    while True:
        time.sleep(0.01)
        w.do(sgl)
        w.show(None)

def main(argv):
    s = Sgf(argv[1])
    play(s)

if __name__ == "__main__":
    import sys
    main(sys.argv)
