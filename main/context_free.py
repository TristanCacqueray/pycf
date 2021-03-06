#!/usr/bin/python -OO
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

""" Context free experiments
"""

import argparse
import time
import sys

from cf_render import cfdg
from cf_ihm import pngwindow, controler
import cf_shapes
from cf_inputs import audio_process, fake_audio_process

# bug pyaudio want to start jackd without this
import pygame
pygame.init()


def print_devices_index():
    import pyaudio
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        devinf = p.get_device_info_by_index(i)
        if devinf['maxInputChannels'] > 0:
            print("%2d: INPUT %s" % (devinf['index'], devinf['name']))
        else:
            print("%2d: OUTPUT %s" % (devinf['index'], devinf['name']))


def quick_render(shapes, output_fmt, fps, wave_path):
    import subprocess
    if len(shapes) > 0:
        render = cfdg((800, 800))
        t0, cpt = time.time(), 0
        print("rendering, please wait")
        for shape in shapes:
            render.do(shape, output_fmt % cpt)
            print("%06d\r" % cpt)
            cpt += 1
        print("%d image rendered in %d seconds" % (cpt, time.time() - t0))
    output_base = output_fmt[:output_fmt.index('%06d')]
    av = ["mencoder", "mf://%s*.png" % output_base,
          "-mf", "fps=%d:type=png" % fps,
          "-ovc", "lavc", "-lavcopts", "vcodec=mpeg4:vbitrate=4096",
          "-oac", "mp3lame", "-audiofile", "%s.wav" % wave_path,
          "-o", "%s.avi" % output_base]
    print("Encoding with: %s" % ' '.join(av))
    if subprocess.Popen(av).wait() != 0:
        print("encodage a plante")
        return
    print("Demo !")
    subprocess.Popen(["mplayer", "%s.avi" % output_base]).wait()


def usage():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--fps", type=int, default=25)
    p.add_argument("--shape", type=int, default=0)
    p.add_argument("--input")
    p.add_argument("--output")
    p.add_argument("--opengl", action="store_true")
    p.add_argument("--render")

    return p.parse_args()


def main():
    # dirty getopt
    args = usage()
    if args.list:
        return print_devices_index()
    if "--gains" in sys.argv:
        idx = sys.argv.index("--gains")
        start_amps = (float(sys.argv[idx+1]),
                      float(sys.argv[idx+2]),
                      float(sys.argv[idx+3]),
                      float(sys.argv[idx+4]))
        del sys.argv[idx:idx+5]
    else:
        start_amps = (1.0, 1.0, 1.0, 1.0)

    if args.opengl:
        import gl_ihm
        import gl_shapes

    render_video = False
    if args.render:
        if args.render.find('%06d') == -1:
            raise RuntimeError("output_fmt must contain %06d")
        render_video = True
        to_render = []

    if args.opengl:
        shapes = gl_shapes.shapes
    else:
        shapes = cf_shapes.shapes

    if args.input:
        input_obj = audio_process(
            input_fd=args.input,
            fps=args.fps,
            output_device_index=args.output,
        )
    else:
        input_obj = fake_audio_process()

    slow_render = False
    if args.opengl:
        render = gl_ihm.window
        viewer = render
    else:
        render = cfdg()
        viewer = pngwindow()
    control = controler(viewer, shapes, args.shape, start_amps)
    t0, cpt = time.time(), 0
    rate = 1 // float(args.fps)
    try:
        gl_cpt = 0
        while True:
            # audio indicateurs (amps, frequencies)
            inputs = input_obj.recv(render_video)
            fft = inputs[4]

            # apply controllers gains
            gains = control.get_gains()
            amps = list(map(lambda x: x*gains[0], inputs[:4]))
            for idx in range(1, len(gains)):
                amps[idx] = amps[idx] * gains[idx]

            shape = control.get_shape()

            # generate shape
            s = shapes[shape].get(amps, fft)

            of = None
            if render_video:
                if args.opengl:
                    of = args.render % gl_cpt
                else:
                    # save shape for further rendering
                    to_render.append(s)

            if control.dump_shape():
                print(s)

            # render image
            t1 = time.time()
            img = render.do(s, of)
            render_time = time.time() - t1
            if render_time - rate > 0.01:
                if not slow_render:
                    print("%f sec to render, %f sec below limit (1/%d)" % (
                        render_time, render_time - rate, args.fps))
                    slow_render = True
                else:
                    slow_render = False

            # display image
            viewer.show(img)

            gl_cpt += 1
            cpt += 1
            if t1 - t0 > 10:
                print("%d Frames generated in 10 seconds" % cpt)
                t0, cpt = t1, 0
    except KeyboardInterrupt:
        pass
#     except Exception, e:
#         print "oups:", e

    # auto render
#     if render_video:
#         if not opengl:
#             viewer.close()
#         quick_render(to_render, output_fmt, fps, infile)

    print("exiting")

if __name__ == "__main__":
    main()
