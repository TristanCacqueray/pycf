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

import time
import sys

import numpy as N

from cf_render import cfdg
from cf_ihm import pngwindow, controler
from cf_shapes import shapes
from cf_inputs import *

def print_devices_index():
	import pyaudio
	p = pyaudio.PyAudio()
	for i in xrange(p.get_device_count()):
		devinf = p.get_device_info_by_index(i)
		if devinf['maxInputChannels'] > 0:
			print "%2d: INPUT %s" % (devinf['index'], devinf['name'])
		else:
			print "%2d: OUTPUT %s" % (devinf['index'], devinf['name'])

def quick_render(shapes, output_fmt, fps, wave_path):
	import subprocess
	if len(shapes) > 0:
		render = cfdg((800, 800))
		t0, cpt = time.time(), 0
		print "rendering, please wait"
		for shape in shapes:
			render.do(shape, output_fmt % cpt)
			print "%06d\r" % cpt,
			cpt += 1
		print "%d image rendered in %d seconds" % (cpt, time.time() - t0)
	output_base = output_fmt[:output_fmt.index('%06d')]
	av = ["mencoder", "mf://%s*.png" % output_base, "-mf", "fps=%d:type=png" % fps,
		"-ovc", "lavc", "-lavcopts", "vcodec=mpeg4:vbitrate=4096",
		"-oac", "mp3lame", "-audiofile", wave_path,
		"-o", "%s.avi" % output_base]
	print "Encoding with: %s" % ' '.join(av)
	if subprocess.Popen(av).wait() != 0:
		print "encodage a plante"
		return
	print "Demo !"
	subprocess.Popen(["mplayer", "%s.avi" % output_base]).wait()

def get_argv(name, default, _type = int):
	if name in sys.argv:
		idx = sys.argv.index(name)
		value = _type(sys.argv[idx+1])
		del sys.argv[idx:idx+2]
	else:
		value = default
	return value
def check_argv(name):
	if name in sys.argv:
		del sys.argv[sys.argv.index(name)]
		return True
	return False


def main():
	# dirty getopt
	if check_argv("--list"):
		return print_devices_index()
	in_dev_idx = get_argv("--input-device", None)
	out_dev_idx = get_argv("--output-device", None)
	fps = get_argv("--fps", 25)

	test_ihm = check_argv("--noinput")
	infile = get_argv("--wave", None, str)

	start_shape = get_argv("--shape", 0)
	if "--gains" in sys.argv:
		idx = sys.argv.index("--gains")
		start_amps = (float(sys.argv[idx+1]),
			float(sys.argv[idx+2]),
			float(sys.argv[idx+3]),
			float(sys.argv[idx+4]))
		del sys.argv[idx:idx+5]
	else:
		start_amps = (1.0, 1.0, 1.0, 1.0)
	opengl = check_argv("--opengl")
	if opengl:
		import gl_ihm
		import gl_shapes

	render_video = False
	output_fmt = get_argv("--render", None, str)
	if output_fmt:
		if output_fmt.find('%06d') == -1:
			raise RuntimeError("output_fmt must contain %06d")
		render_video = True
		to_render = []

	while len(sys.argv) > 1:
		if sys.argv[1] in shapes[start_shape].params.keys():
			shapes[start_shape].params[sys.argv[1]].value = float(sys.argv[2])
			del sys.argv[1:3]
		else:
			break


	if len(sys.argv) != 1:
		raise RuntimeError("Unknown parameters: %s" % sys.argv[1:])
	
	if test_ihm:
		input = fake_audio_process()
	else:
		input = audio_process(
			infile = infile,
			fps = fps,
			input_device_index = in_dev_idx,
			output_device_index = out_dev_idx
		)

	slow_render = False
	if opengl:
		render = gl_ihm.window
		viewer = render
		shapes = gl_shapes.shapes
	else:
		render = cfdg()
		viewer = pngwindow()
	control = controler(viewer, shapes, start_shape, start_amps)
	t0, cpt = time.time(), 0
	rate = 1/float(fps)
	try:
		gl_cpt = 0
		while True:
			# audio indicateurs (amps, frequencies)
			inputs = input.recv(render_video)
			fft = inputs[4]

			# apply controllers gains
			gains = control.get_gains()
			amps = map(lambda x: x*gains[0], inputs[:4])
			for idx in xrange(1, len(gains)):
				amps[idx] = amps[idx] * gains[idx]

			shape = control.get_shape()

			# generate shape
			s = shapes[shape].get(amps, fft)

			of = None
			if render_video:
				if opengl:
					of = output_fmt % gl_cpt
				else:
					# save shape for further rendering
					to_render.append(s)

			if control.dump_shape():
				print s

			# render image
			t1 = time.time()
			img = render.do(s, of)
			render_time = time.time() - t1
			if render_time - rate > 0.01:
				if not slow_render:
					print "%f sec to render, %f sec below limit (1/%d)" % (
						render_time, render_time - rate, fps)
					slow_render = True
				else:
					slow_render = False

			# display image
			viewer.show(img)

			gl_cpt += 1
			cpt += 1
			if t1 - t0 > 10:
				print "%d Frames generated in 10 seconds" % cpt
				t0, cpt = t1, 0
	except KeyboardInterrupt:
		pass
#	except Exception, e:
#		print "oups:", e
	if render_video:
		if not opengl:
			viewer.close()
		quick_render(to_render, output_fmt, fps, infile)

	print "exiting"


if __name__ == "__main__":
	main()

