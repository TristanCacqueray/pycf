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

from multiprocessing import Process, Pipe, Queue
from Queue import Full
import pyaudio
import wave
import numpy as N
from cf_dsp import dsp


class wave_reader:
	def __init__(self, infile, frames_per_buffer = 4410):
		print "Opening '%s' file..."%infile,
		self.f = wave.open(infile, 'rb')
		rate = self.f.getframerate()
		sampwidth = self.f.getsampwidth()
		channels = self.f.getnchannels()
		print "fmt %d, %d Hz stream of %d size (%d channel)" % (sampwidth, rate, frames_per_buffer, channels)
		if channels > 1:
			raise RuntimeError("Only mono input wave file")
		self.eq = eq(rate, sampwidth, frames_per_buffer)
		self.frames_per_buffer = frames_per_buffer
		self.params = []
	def recv(self):
		if len(self.params) > 0:
			return self.params.pop()
		data = self.f.readframes(self.frames_per_buffer)
		if data == '':
			return None
		for param in self.eq.gen(data):
			self.params.insert(0, param)
		return self.params.pop()

class wave_file:
	def __init__(self, wf):
		self.wf = wave.open(wf, 'rb')
		self.rate = self.wf.getframerate()
		self.channels = self.wf.getnchannels()
		self.format = self.wf.getsampwidth()
	def read(self, frames_per_buffer):
		data = self.wf.readframes(frames_per_buffer)
		if data == '':
			raise KeyboardInterrupt
		return data
	def close(self):
		self.wf.close()

class fake_audio_process:
	def __init__(self, *arg):
		self.cpt = 0
	def recv(self, mode = None):
		#time.sleep(0.5)
		if self.cpt & 1:
			return (0.9, 0.9, 0.9, 0.9, N.random.random(886)/10.0)
		self.cpt += 1
		return (0.0, 0.0, 0.0, 0.0, N.random.random(886)/10.0)

class audio_process:
	def __init__(self, fps = 25, input_device_index = None, infile = None, output_device_index = None):
		self.q = Queue(4096 * 4096)
		self.rate = 44100 	# hardcoded 44100 Hz sample rate
		if self.rate / float(fps) != self.rate / fps:
			raise RuntimeError("Frame per second must be a multiple of %d" % self.rate)
		self.frames_per_buffer = self.rate / fps
		self.input_device_index = input_device_index
		self.output_device_index = output_device_index
		self.infile = infile
		p = Process(target=self.run, args=())
		p.start()
	def process(self):
		while True:
			data = self.input_stream.read(self.frames_per_buffer)
			self.q.put_nowait(self.dsp.gen(data))
			if self.output_stream:
				self.output_stream.write(data)
	def get_device_name(self, idx):
		if not idx:
			return "default"
		return self.p.get_device_info_by_index(idx)['name']
	def check_input_stream(self):
		if self.input_stream.rate != self.rate:
			raise RuntimeError("Bad input sample rate %d, only %d supported" %
					(self.input_stream.rate, self.rate))
		if self.input_stream.channels != 1:
			raise RuntimeError("Only mono input supported")
		if self.input_stream.format != 2:
			raise RuntimeError("Only paInt16 sample format supported")
	def open_stream(self, input = False, output = False):
		return self.p.open(format = pyaudio.paInt16,
			channels = 1,
			rate = self.rate,
			output = output,
			input = input,
			output_device_index = self.output_device_index,
			input_device_index = self.input_device_index,
			frames_per_buffer = self.frames_per_buffer)
	def run(self):
		import pyaudio
		import os
		try:
			os.nice(-5)
		except OSError:
			print "Could not set high priority on audio processing, beware of input overflow"
		self.dsp = dsp()
		self.p = pyaudio.PyAudio()

		if self.infile:
			self.input_stream = wave_file(self.infile)
			self.check_input_stream()
			print "Input stream: '%s' format %d bytes, rate %d Hz, %d channels" % (
				self.infile, self.input_stream.format, self.input_stream.rate,
				self.input_stream.channels
			)

			print "Opening Output stream: '%s'" % self.get_device_name(self.output_device_index)
			self.output_stream = self.open_stream(output = True)
		#	self.output_stream = None
		else:
			print "Opening Input stream: '%s' paInt16 %d Hz stream of %d size" % (
					self.get_device_name(self.input_device_index),
					self.rate, self.frames_per_buffer)
			self.input_stream = self.open_stream(input = True)
			self.output_stream = None

		while True:
			try:
				self.process()
			except IOError, e:
				print "IOError:", e
			except Full, e:
				print "The queue is full!"
			except KeyboardInterrupt:
				break
		print "Closing streams"
		self.input_stream.close()
		if self.output_stream:
			self.output_stream.close()
		self.p.terminate()
	def recv(self, render_video = None):
		if not render_video and self.q.qsize() > 3:
			print "Processing too slow - %d frames late, flushing..." % self.q.qsize()
			try:
				while True:
					self.q.get(False)
			except:
				pass
		return self.q.get()
