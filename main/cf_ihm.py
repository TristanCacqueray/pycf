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

from PIL import Image, ImageTk 
import Tkinter as Tk
class pngwindow:
	""" Simple tk image display """
	def __init__(self):
		self.root = Tk.Tk() 
		self.img = None
	def show(self, img):
		pil_img = Image.open(img)
		if not self.img:
			self.img = ImageTk.PhotoImage(pil_img)
			label = Tk.Label(image=self.img) 
			label.grid(columnspan=3, row=0, column=0)
		self.img.paste(pil_img)
		self.root.update()
	def close(self):
		self.root.destroy()

# Controler
class controler:
	def __init__(self, main_app, shapes, start_shape = 0, start_amps = (1.0, 1.0, 1.0, 1.0)):
		self.root = main_app.root
		self.shapes = shapes
		self.shape = Tk.IntVar()
		self.shape.set(start_shape)
		self.dumpshape = Tk.IntVar()

		for idx in xrange(len(shapes)):
			r = Tk.Radiobutton(self.root, text=shapes[idx].name, variable=self.shape, value=idx)
			r.bind("<ButtonRelease-1>", self.shape_clic)
			r.grid(row=1+idx, column=0)
		Tk.Checkbutton(self.root, text="Dump shape", variable=self.dumpshape).grid(row=2+idx, column=0)

		gains = ("master", "low", "mid", "high")
		self.gains = []
		for idx in xrange(len(gains)):
			Tk.Label(self.root, text="%s:" % gains[idx]).grid(row=idx+1, column=1, sticky=Tk.E)#pack(side=Tk.LEFT)
			self.gains.append(Tk.Scale(self.root,
				from_=0, to=3, resolution=0.1,
				orient=Tk.HORIZONTAL, length=300))
			self.gains[idx].set(start_amps[idx])
			self.gains[idx].grid(row=idx+1, column=2, sticky=Tk.E)# pack(side=Tk.LEFT)

		self.params = []
		for idx in xrange(5):
			self.params.append((Tk.Scale(self.root,
				from_=0, to=127, resolution=1,
				orient=Tk.VERTICAL, length=300),
				Tk.Label(self.root, text="        ")))
			self.params[idx][0].grid(row=0, column=idx+3)
			self.params[idx][0].bind("<ButtonRelease-1>", self.param_clic)
			self.params[idx][1].grid(row=1, column=idx+3, sticky=Tk.E)
		self.reset_param()
		self.root.update()
	
	def param_clic(self, ev):
		self.apply_param()

	def shape_clic(self, ev):
		self.reset_param()
		
	def apply_param(self):
		shape = self.shapes[self.shape.get()]
		shape_params = sorted(shape.params.keys())
		for idx in xrange(len(shape_params)):
			shape.params[shape_params[idx]].value = self.params[idx][0].get()
		
	def reset_param(self):
		idx = 0
		shape = self.shapes[self.shape.get()]
		shape_params = sorted(shape.params.keys())
		while idx < len(shape_params):
			param = shape.params[shape_params[idx]]
			self.params[idx][0].config(from_=param.range[0],
				to=param.range[1],
				resolution=param.resolution)
			self.params[idx][0].set(param.value)
			self.params[idx][1].config(text=shape_params[idx])
			idx += 1
		while idx < len(self.params):
			self.params[idx][0].set(0)
			self.params[idx][1].config(text=" ")
			idx += 1
	def get_shape(self):
		return self.shape.get()
	def get_gains(self):
		return (self.gains[0].get(), self.gains[1].get(), self.gains[2].get(), self.gains[3].get())
	def dump_shape(self):
		if self.dumpshape.get():
			self.dumpshape.set(0)
			return 1
		return 0


