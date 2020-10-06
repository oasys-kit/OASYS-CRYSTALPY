#! /usr/bin/env python3

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'OASYS1-CRYSTALPY'

VERSION = '1.1'
ISRELEASED = False

DESCRIPTION = 'Oasys interface for crystalpy'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Edoardo Cappelli, Mark Glass and Manuel Sanchez del Rio'
AUTHOR_EMAIL = 'srio@esrf.eu'
URL = 'https://github.com/oasys-kit/OASYS-CRYSTALPY'
DOWNLOAD_URL = 'https://github.com/oasys-kit/OASYS-CRYSTALPY'
LICENSE = 'MIT'

KEYWORDS = (
    'xray',
    'dynamic diffraction',
    'polarization',
    'Oasys',
    'Orange',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Cython',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research',
)


SETUP_REQUIRES = (
                  'setuptools',
                  )

INSTALL_REQUIRES = (
                    'oasys1',
                    'crystalpy',
                   )


PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
    "orangecontrib.crystalpy.widgets.elements": ["icons/*.png", "icons/*.jpg"],
}


NAMESPACE_PACKAGES = ["orangecontrib", "orangecontrib.crystalpy", "orangecontrib.crystalpy.widgets"]


ENTRY_POINTS = {
    'oasys.addons': ("CrystalPy = orangecontrib.crystalpy", ),
    'oasys.widgets': (
        "CrystalPy = orangecontrib.crystalpy.widgets.elements",
    ),
}

if __name__ == '__main__':
    try:
        import PyMca5, PyQt4

        raise NotImplementedError("This version of SRW doesn't work with Oasys1 beta.\nPlease install OASYS1 final release: https://www.aps.anl.gov/Science/Scientific-Software/OASYS")
    except:
        setup(
              name=NAME,
              version=VERSION,
              description=DESCRIPTION,
              long_description=LONG_DESCRIPTION,
              author=AUTHOR,
              author_email=AUTHOR_EMAIL,
              url=URL,
              download_url=DOWNLOAD_URL,
              license=LICENSE,
              keywords=KEYWORDS,
              classifiers=CLASSIFIERS,
              packages=PACKAGES,
              package_data=PACKAGE_DATA,
              setup_requires=SETUP_REQUIRES,
              install_requires=INSTALL_REQUIRES,
              entry_points=ENTRY_POINTS,
              namespace_packages=NAMESPACE_PACKAGES,
              include_package_data=True,
              zip_safe=False,
              )
