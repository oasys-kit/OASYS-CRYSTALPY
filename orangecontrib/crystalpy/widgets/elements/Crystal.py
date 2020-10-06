import numpy as np
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources

import sys
import os

from crystalpy.diffraction.DiffractionSetup import DiffractionSetup
from crystalpy.diffraction.Diffraction import Diffraction
from crystalpy.diffraction.GeometryType import BraggDiffraction, BraggTransmission, LaueDiffraction, LaueTransmission
from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch


class OWCrystal(widget.OWWidget):
    name = "Crystal"
    id = "orange.widgets.dataCrystal"
    description = "Application to compute..."
    icon = "icons/Crystal.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 25
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "Crystal"]

    # the widget takes in a collection of Photon objects and
    # sends out an object of the same type made up of scattered photons.
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "handler": "_set_input",
               "doc": ""}]

    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "transfer diffraction results"},
               ]

    want_main_area = False

    GEOMETRY_TYPE = Setting(0)         # Bragg diffraction
    CRYSTAL_NAME = Setting(0)          # Si
    THICKNESS = Setting(0.01)          # centimeters
    MILLER_H = Setting(1)              # int
    MILLER_K = Setting(1)              # int
    MILLER_L = Setting(1)              # int
    ASYMMETRY_ANGLE = Setting(0.0)     # degrees
    AZIMUTHAL_ANGLE = Setting(90.0)    # degrees
    INCLINATION_ANGLE = Setting(45.0)  # degrees
    DUMP_TO_FILE = Setting(1)          # Yes
    FILE_NAME = Setting("crystal.dat")

    def __init__(self):
        super().__init__()

        self._input_available = False

        # Define a tuple of crystals to choose from.
        self.crystal_names = ("Si", "Ge", "Diamond")

        box0 = gui.widgetBox(self.controlArea, " ", orientation="horizontal")
        # widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.compute)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)

        box = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        idx = -1

        # widget index 0
        idx += 1
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "GEOMETRY_TYPE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["Bragg diffraction", "Bragg transmission", "Laue diffraction", "Laue Transmission"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)
        
        # widget index 1
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "CRYSTAL_NAME",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=['Si', 'Ge', 'Diamond'],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 2
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "THICKNESS",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 3
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_H",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 4
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_K",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 5
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_L",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 6
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ASYMMETRY_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 7
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "AZIMUTHAL_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 8
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "INCLINATION_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["No", "Yes"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)
        
        # widget index 10
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        print("Crystal: Crystal initialized.\n")

        gui.rubber(self.controlArea)

    def _set_input(self, photon_bunch):
        if photon_bunch is not None:
            self._input_available = True
            self.incoming_bunch = photon_bunch
            self.compute()

    def unitLabels(self):
        return ["Geometry type", "Crystal name", "Thickness [cm]", "Miller H", "Miller K", "Miller L",
                "Asymmetry angle [deg]", "Azimuthal angle [deg]",
                "Inclination angle [deg]", "Dump to file", "File name"]

    def unitFlags(self):
        return ["True",          "True",         "True",           "True",     "True",     "True",
                "True",                  "True",
                "True",                    "True",         "self.DUMP_TO_FILE == 1"]

    def compute(self):

        if not self._input_available:
            raise Exception("Crystal: Input data not available!\n")

        # Translate CRYSTAL_TYPE (int) into a crystal name (string).
        CRYSTAL_NAME = self.crystal_names[self.CRYSTAL_NAME]

        outgoing_bunch = OWCrystal.calculate_external_Crystal(GEOMETRY_TYPE=self.GEOMETRY_TYPE,
                                                                       CRYSTAL_NAME=CRYSTAL_NAME,
                                                                       THICKNESS=self.THICKNESS,
                                                                       MILLER_H=self.MILLER_H,
                                                                       MILLER_K=self.MILLER_K,
                                                                       MILLER_L=self.MILLER_L,
                                                                       ASYMMETRY_ANGLE=self.ASYMMETRY_ANGLE,
                                                                       AZIMUTHAL_ANGLE=self.AZIMUTHAL_ANGLE,
                                                                       incoming_bunch=self.incoming_bunch,
                                                                       INCLINATION_ANGLE=self.INCLINATION_ANGLE,
                                                                       DUMP_TO_FILE=self.DUMP_TO_FILE,
                                                                       FILE_NAME=self.FILE_NAME)

        self.send("photon bunch", outgoing_bunch)
        print("Crystal: The results were sent to the viewer.\n")

    def defaults(self):
        self.resetSettings()
        self.compute()
        return

    def get_doc(self):
        print("Crystal: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.crystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'CrystalActive'+'.txt')
        print("Crystal: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("Crystal: sys.platform did not yield an acceptable value!\n")
        os.system(command)

    @staticmethod
    def calculate_external_Crystal(GEOMETRY_TYPE,
                                          CRYSTAL_NAME,
                                          THICKNESS,
                                          MILLER_H,
                                          MILLER_K,
                                          MILLER_L,
                                          ASYMMETRY_ANGLE,
                                          AZIMUTHAL_ANGLE,
                                          incoming_bunch,
                                          INCLINATION_ANGLE,
                                          DUMP_TO_FILE,
                                          FILE_NAME="tmp.dat"):

        # Create a GeometryType object:
        #     Bragg diffraction = 0
        #     Bragg transmission = 1
        #     Laue diffraction = 2
        #     Laue transmission = 3
        if GEOMETRY_TYPE == 0:
            GEOMETRY_TYPE_OBJECT = BraggDiffraction()

        elif GEOMETRY_TYPE == 1:
            GEOMETRY_TYPE_OBJECT = BraggTransmission()

        elif GEOMETRY_TYPE == 2:
            GEOMETRY_TYPE_OBJECT = LaueDiffraction()

        elif GEOMETRY_TYPE == 3:
            GEOMETRY_TYPE_OBJECT = LaueTransmission()

        else:
            raise Exception("Crystal: The geometry type could not be interpreted!\n")

        # Create a diffraction setup.
        # At this stage I translate angles in radians, energy in eV and all other values in SI units.
        print("Crystal: Creating a diffraction setup...\n")

        diffraction_setup = DiffractionSetup(geometry_type=GEOMETRY_TYPE_OBJECT,  # GeometryType object
                                             crystal_name=str(CRYSTAL_NAME),  # string
                                             thickness=float(THICKNESS) * 1e-2,  # meters
                                             miller_h=int(MILLER_H),  # int
                                             miller_k=int(MILLER_K),  # int
                                             miller_l=int(MILLER_L),  # int
                                             asymmetry_angle=float(ASYMMETRY_ANGLE) / 180 * np.pi,  # radians
                                             azimuthal_angle=float(AZIMUTHAL_ANGLE) / 180 * np.pi)  # radians
                                             # incoming_photons=incoming_bunch)

        # Create a Diffraction object.
        diffraction = Diffraction()

        # Create a PolarizedPhotonBunch object holding the results of the diffraction calculations.
        print("Crystal: Calculating the outgoing photons...\n")
        outgoing_bunch = diffraction.calculateDiffractedPolarizedPhotonBunch(diffraction_setup,
                                                                    incoming_bunch,
                                                                    INCLINATION_ANGLE)

        # Check that the result of the calculation is indeed a PolarizedPhotonBunch object.
        if not isinstance(outgoing_bunch, PolarizedPhotonBunch):
            raise Exception("Crystal: Expected PolarizedPhotonBunch as a result, found {}!\n".format(type(outgoing_bunch)))

        # Dump data to file if requested.
        if DUMP_TO_FILE == 0:

            print("Crystal: Writing data in {file}...\n".format(file=FILE_NAME))

            with open(FILE_NAME, "w") as file:
                try:
                    file.write("#S 1 photon bunch\n"
                               "#N 8\n"
                               "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3\n")
                    file.write(outgoing_bunch.toString())
                    file.close()
                    print("File written to disk: %s"%FILE_NAME)
                except:
                    raise Exception("Crystal: The data could not be dumped onto the specified file!\n")

        return outgoing_bunch


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWCrystal()
    w.show()
    app.exec()
    w.saveSettings()
