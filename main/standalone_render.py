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

import os
from cf_inputs import wave_file
from cf_dsp import dsp,impAmps
from cf_shapes import twist,triburn


def usage(argv):
    print("usage: %s wave_file" % argv[0])
    return 1


def main(argv):
    plot = False
    if "plot" in argv:
        import subprocess
        argv.pop(argv.index("plot"))
        plot = True
    wave_path = argv[1]
    if not os.path.isfile(wave_path):
        return usage(argv)
    if not os.path.exists("/tmp/cfdg"):
        os.mkdir("/tmp/cfdg")
    base_path = "/tmp/cfdg/%s" % '.'.join(
            os.path.basename(wave_path).split('.')[:-1])

    if plot:
        ostats = [ ]
        for i in range(4):
            ostats.append(open("/tmp/pycf%d" % i, "w"))
        ofluid_stats = []
        for i in range(4):
            ofluid_stats.append(open("/tmp/pycf%d_fluid" % i, "w"))

    shape = triburn()
    filters = dsp()
    try:
        frames_per_buffer = 44100 / 25
        input_stream = wave_file(wave_path)
        while True:
            data = input_stream.read(frames_per_buffer)
            stats = filters.gen(data)
            fluid_stats.impulse(stats)
            open("%s_%05d.cfdg" % (base_path, idx), "w").write(
                shape.get(stats[:4], None)
            )
            if plot:
                for i in range(4):
                    ostats[i].write("%f\n" % stats[i])
                    ofluid_stats[i].write("%f\n" % fluid_stats[i])

    except KeyboardInterrupt:
        pass

    if plot:
        p = subprocess.Popen("gnuplot", stdin=subprocess.PIPE)
        cmd = ["plot"]
        for i in [1, 2, 3]:
                #     cmd.append("'/tmp/pycf%d' with lines," % i)
            cmd.append("'/tmp/pycf%d_fluid' with lines," % i)
        cmd[-1] = cmd[-1][:-1]
        p.stdin.write(" ".join(cmd)+"\n")
        input("press enter when done")
        p.terminate()

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
