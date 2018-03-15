import sys

if len(sys.argv) < 2:
	print 'Please include the node_id as an argument. E.g. python node_id.py 47620'

n = int(sys.argv[1])

b = bin(n)
print 'Given: ' + sys.argv[1]
print eval(b[0:10])
print eval('0b' + b[10:])