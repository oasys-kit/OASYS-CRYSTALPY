"""
Unittest for PhotonBunch class.
"""
import unittest

from crystalpy.util.Vector import Vector

from crystalpy.polarization.StokesVector import StokesVector

from orangecontrib.crystalpy.util.PhotonBunch import PolarizedPhoton
from orangecontrib.crystalpy.util.PhotonBunch import PhotonBunch


class PhotonBunchTest(unittest.TestCase):

    def setUp(self):
        photon1_1 = PolarizedPhoton(8000, Vector(1, 1, 0), StokesVector([1, 0, 0, -1]))
        photon1_2 = PolarizedPhoton(254, Vector(1, 0.52, 1e-6), StokesVector([1e+8, 0, 0, -1]))
        photon1_3 = PolarizedPhoton(1e+5, Vector(2.00, 1, 0), StokesVector([1, 0.9002, 0, -1e-5]))
        self.photon_bunch1 = PhotonBunch([photon1_1, photon1_2, photon1_3])

        # quasi-monochromatic bunch.
        photon2_1 = PolarizedPhoton(8000.0000, Vector(1, 1, 0), StokesVector([1, 0, 0, -1]))
        photon2_2 = PolarizedPhoton(8000.0000, Vector(0.5, 0.5, 1e-6), StokesVector([1e+8, 0, 0, -1]))
        photon2_3 = PolarizedPhoton(8000.0001, Vector(1.0, 1, 0), StokesVector([1, 0.9002, 0, -1e-5]))
        self.photon_bunch2 = PhotonBunch([photon2_1, photon2_2, photon2_3])

        # quasi-unidirectional bunch.
        photon3_1 = PolarizedPhoton(8000, Vector(1, 1, 0), StokesVector([1, 0, 0, -1]))
        photon3_2 = PolarizedPhoton(254, Vector(0.50, 0.50, 0), StokesVector([1e+8, 0, 0, -1]))
        photon3_3 = PolarizedPhoton(1e+5, Vector(0.20000001, 0.20000, 0), StokesVector([1, 0.9002, 0, -1e-5]))
        self.photon_bunch3 = PhotonBunch([photon3_1, photon3_2, photon3_3])

    def test_constructor(self):
        self.assertIsInstance(self.photon_bunch1.photon_bunch, list)
        self.assertIsInstance(self.photon_bunch1.photon_bunch[0], PolarizedPhoton)
        self.assertEqual(self.photon_bunch1.photon_bunch,
                         [PolarizedPhoton(8000, Vector(1, 1, 0), StokesVector([1, 0, 0, -1])),
                          PolarizedPhoton(254, Vector(1, 0.52, 1e-6), StokesVector([1e+8, 0, 0, -1])),
                          PolarizedPhoton(1e+5, Vector(2.00, 1, 0), StokesVector([1, 0.9002, 0, -1e-5]))])
        print(self.photon_bunch2.photon_bunch[1].energy(), self.photon_bunch2.photon_bunch[1].unitDirectionVector().components())
        print(Vector(1, 0.52, 1e-6).getNormalizedVector().components())
        self.assertTrue(self.photon_bunch2.photon_bunch[1] ==
                        PolarizedPhoton(8000.0000, Vector(1, 0.52, 1e-6), StokesVector([1e+8, 0, 0, -1])))

    def test_add(self):
        photon_bunch1 = self.photon_bunch1
        photon_bunch2 = self.photon_bunch2

        to_be_added = [PolarizedPhoton(2000, Vector(1, 1, 0), StokesVector([1, 1, 0, 0])),
                       PolarizedPhoton(3456, Vector(2, 1, 0), StokesVector([1, 1, 0, -1]))]

        photon_bunch1.add(to_be_added)  # list
        photon_bunch2.add(to_be_added[1])  # single element

        self.assertIsInstance(photon_bunch1, PhotonBunch)
        self.assertIsInstance(photon_bunch2, PhotonBunch)
        self.assertIsInstance(photon_bunch1[3], PolarizedPhoton)
        self.assertTrue(photon_bunch1[3] == PolarizedPhoton(2000, Vector(1, 1, 0), StokesVector([1, 1, 0, 0])))
        self.assertTrue(photon_bunch2[3] == PolarizedPhoton(3456, Vector(2, 1, 0), StokesVector([1, 1, 0, -1])))
        self.assertEqual(len(photon_bunch1), 5)
        self.assertEqual(len(photon_bunch2), 4)

    def test_len(self):
        self.assertIsInstance(len(self.photon_bunch1), int)
        self.assertEqual(len(self.photon_bunch1), 3)

    def test_iter(self):
        list_iterator = iter(self.photon_bunch1.photon_bunch)
        for photon in self.photon_bunch1:
            self.assertTrue(photon == next(list_iterator))

    def test_getitem(self):
        self.assertIsInstance(self.photon_bunch1[0], PolarizedPhoton)
        self.assertTrue(self.photon_bunch1[1] == self.photon_bunch1.photon_bunch[1])

    def test_is_monochromatic(self):
        self.assertFalse(self.photon_bunch1.is_monochromatic(0))
        self.assertTrue(self.photon_bunch2.is_monochromatic(3))
        self.assertFalse(self.photon_bunch2.is_monochromatic(4))

    def test_is_unidirectional(self):
        self.assertFalse(self.photon_bunch1.is_unidirectional())
        self.assertTrue(self.photon_bunch3.is_unidirectional())
        self.assertFalse(self.photon_bunch2.is_unidirectional())
