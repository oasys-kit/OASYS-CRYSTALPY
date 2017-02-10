print('Hello world')
print(dir(in_object_1._beam))
vx = in_object_1._beam.getshcol(4,nolost=1)
vy = in_object_1._beam.getshcol(5,nolost=1)
vz = in_object_1._beam.getshcol(6,nolost=1)

s0 = in_object_1._beam.getshcol(30,nolost=1)
s1 = in_object_1._beam.getshcol(31,nolost=1)
s2 = in_object_1._beam.getshcol(32,nolost=1)
s3 = in_object_1._beam.getshcol(33,nolost=1)

energy = in_object_1._beam.getshcol(11,nolost=1)