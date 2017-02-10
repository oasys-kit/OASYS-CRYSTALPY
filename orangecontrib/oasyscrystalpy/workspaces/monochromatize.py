
wavenumber = in_object_1._beam.rays[:,10]
print("Monochromatizing to the average: ",wavenumber.mean())
in_object_1._beam.rays[:,10] = wavenumber.mean()

out_object = in_object_1