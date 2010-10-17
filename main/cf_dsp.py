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

# Signal processing
try:
	import scipy.signal.filter_design as fd
	import scipy.signal.signaltools as st
except ImportError:
	print "No scipy found, please install-it for audio filter"
	class fd:
		@staticmethod
		def iirdesign(*argv, **kw):	return (0, 0)
	class st:
		@staticmethod
		def lfiltic(*argv):		return 0
		@staticmethod
		def lfilter(a, b, data, zi):	return data

import numpy as N
import struct
import wave
class Filter:
	def __init__(self, bpass, bstop, ftype='butter'):
		self.b, self.a = fd.iirdesign(bpass, bstop, 1, 100, ftype=ftype, output='ba')
		self.ic = st.lfiltic(self.b, self.a, (0.0,))
	def filter(self, data):
		res = st.lfilter(self.b, self.a, data, zi=self.ic)
		self.ic = res[-1]
		return res[0]

class dsp:
	def __init__(self):
		self.max = float((2 ** (2 * 8)) / 2)
		# really dirty filters...
		self.lpass = Filter(0.01, 0.1, ftype='ellip')
		self.mpass = Filter((0.1, 0.2),  (0.05, 0.25), ftype='ellip')
		self.hpass = Filter(0.2, 0.1, ftype='ellip')
	
	def gen(self, data):
		# convert to numeric [-1; 1]
		wav = N.fromstring(data, N.int16) / self.max
		fftlen = 2048
		reallen = fftlen / 2
		return (
			N.max(N.abs(wav)),
			N.max(N.abs(self.lpass.filter(wav))),
			N.max(N.abs(self.mpass.filter(wav))),
			N.max(N.abs(self.hpass.filter(wav))),
			N.abs(N.fft.fft(wav, fftlen)[:reallen], ) / reallen
		)

class impAmps:
	""" Convert amps to impulse """
	def __init__(self):
		self.amps = N.zeros(4)
	def impulse(self, amps, delay = 10.0):
		for i in xrange(4):
			if amps[i] >= self.amps[i]:
				self.amps[i] = amps[i]
			else:
				delta = (self.amps[i] - amps[i]) / delay
				self.amps[i] -= delta
		return self.amps
	def __getitem__(self, item):
		return self.amps[item]
