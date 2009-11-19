a = [5, 4, 5, 0, 1, 2, 3, 0, 3]

b = [0, 0]

print "a:",a
print "b:",
dx = 0
ratio = len(a) / float(len(b))
print ratio
for x in xrange(len(b)):
	dx = int(x*ratio)
	dx1 = int((x+1)*ratio)
	print dx, dx1
	b[x] = sum(a[dx:dx1])
print b
