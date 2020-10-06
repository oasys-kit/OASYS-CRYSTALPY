"""
Unittest for PolarizedPhoton class.
"""
import unittest

from crystalpy.util.Vector import Vector

from crystalpy.polarization.StokesVector import StokesVector

from orangecontrib.crystalpy.util.PhotonBunch import PolarizedPhoton


class PolarizedPhotonTest(unittest.TestCase):

    def setUp(self):
        self.energy_in_ev = 8000
        self.direction_vector = Vector(1, 3, 2).getNormalizedVector()
        self.stokes_vector = StokesVector([1, -1, 0, 0])
        self.polarized_photon = PolarizedPhoton(self.energy_in_ev,
                                                self.direction_vector,
                                                self.stokes_vector)

    def test_constructor(self):
        candidate = self.polarized_photon._stokes_vector
        self.assertIsInstance(candidate, StokesVector)
        self.assertEqual(candidate, self.stokes_vector)

    def test_stokesVector(self):
        candidate = self.polarized_photon.stokesVector()
        self.assertIsInstance(candidate, StokesVector)
        self.assertEqual(candidate, self.stokes_vector)

    def test_operator_equal(self):
        candidate = PolarizedPhoton(8000.00, Vector(0.5, 1.5, 1.0), StokesVector([1.0, -1.0, 0.0, 0.0]))
        candidate1 = PolarizedPhoton(8000.01, Vector(0.5000002, 1.5, 1.0), StokesVector([1.0 + 1e-4, -1.0, 0.0, 0.0]))
        self.assertTrue(self.polarized_photon == candidate)
        self.assertFalse(self.polarized_photon == candidate1)

    def test_operator_not_equal(self):
        candidate = PolarizedPhoton(8000.00, Vector(0.5, 1.5, 1.0), StokesVector([1.0, -1.0, 0.0, 0.0]))
        candidate1 = PolarizedPhoton(8000.01, Vector(0.5000002, 1.5, 1.0), StokesVector([1.0 + 1e-4, -1.0, 0.0, 0.0]))
        self.assertTrue(self.polarized_photon != candidate1)
        self.assertFalse(self.polarized_photon != candidate)
