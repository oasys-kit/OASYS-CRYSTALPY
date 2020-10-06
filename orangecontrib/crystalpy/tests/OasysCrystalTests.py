import unittest

from orangecontrib.crystalpy.tests.util.PhotonBunchTest import PhotonBunchTest
from orangecontrib.crystalpy.tests.util.PolarizedPhotonTest import PolarizedPhotonTest


def suite():
    """
    Gathers all the tests in a test suite.
    """
    suites = (
        unittest.makeSuite(PolarizedPhotonTest, "test"),
        unittest.makeSuite(PhotonBunchTest, "test")
    )
    return unittest.TestSuite(suites)

if __name__ == "__main__":

    unittest.main(defaultTest="suite")
