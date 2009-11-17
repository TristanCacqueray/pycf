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

# RENDERER
import cStringIO
import subprocess
class cfdg:
	""" ContextFree process manager """
	def __init__(self, dim = (300, 300)):
		self.p = None
		self.argv = ["cfdg", "-q", "-w", str(dim[0]), "-h", str(dim[1]), "-", "/proc/self/fd/1"]
	def do(self, shape, output = None):
		""" Return the png file in a cStringIO """
		if output:
			self.argv[-1] = output
		self.p = subprocess.Popen(self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		self.p.stdin.write(shape)
		self.p.stdin.close()
		if output:
			return
		out = cStringIO.StringIO(self.p.stdout.read())
		if self.p.wait() != 0:
			print "cfdg a plante: [%s]" % shape
		return out
