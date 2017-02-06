import numpy as np
from PyQt4.QtGui import QIntValidator, QDoubleValidator, QApplication, QSizePolicy
# from PyMca5.PyMcaIO import specfilewrapper as specfile
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources
import sys
import os
from crystalpy.diffraction.DiffractionSetup import DiffractionSetup
from crystalpy.diffraction.Diffraction import Diffraction
from crystalpy.diffraction.GeometryType import BraggDiffraction, BraggTransmission, LaueDiffraction, LaueTransmission
from crystalpy.polarization.MuellerDiffraction import MuellerDiffraction
from crystalpy.polarization.StokesVector import StokesVector
from crystalpy.util.PhotonBunch import PhotonBunch


class OWCrystalPassive(widget.OWWidget):
    name = "CrystalPassive"
    id = "orange.widgets.dataCrystalPassive"
    description = "Application to compute..."
    icon = "icons/Crystal.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 10
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "CrystalPassive"]

    # the widget takes in a collection of Photon objects and
    # sends out an object of the same type made up of scattered photons.
    inputs = [{"name": "photon bunch",
               "type": PhotonBunch,
               "handler": "_set_input",
               "doc": ""}]

    outputs = [{"name": "photon bunch",
                "type": PhotonBunch,
                "doc": "transfer diffraction results"},
               # another possible output
               # {"name": "oasyscrystalpy-file",
               #  "type": str,
               #  "doc": "transfer a file"},
               ]

    want_main_area = False

    GEOMETRY_TYPE = Setting(0)  # Bragg diffraction
    CRYSTAL_NAME = Setting(0)  # Si
    THICKNESS = Setting(0.01)  # centimeters
    MILLER_H = Setting(1)  # int
    MILLER_K = Setting(1)  # int
    MILLER_L = Setting(1)  # int
    ASYMMETRY_ANGLE = Setting(0.0)  # degrees
    AZIMUTHAL_ANGLE = Setting(90.0)  # degrees
    INCLINATION_ANGLE = Setting(45.0)  # degrees
    DUMP_TO_FILE = Setting(1)  # No
    FILE_NAME = Setting("crystal_passive.dat")

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
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 3
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_H",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 4
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_K",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 5
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "MILLER_L",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 6
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ASYMMETRY_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 7
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "AZIMUTHAL_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 8
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "INCLINATION_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["Yes", "No"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)
        
        # widget index 10
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        print("CrystalPassive: Passive crystal initialized.\n")

        gui.rubber(self.controlArea)

    def _set_input(self, photon_bunch):
        if photon_bunch is not None:
            self._input_available = True
            self.incoming_bunch = photon_bunch

    def unitLabels(self):
        return ["Geometry type", "Crystal name", "Thickness [cm]", "Miller H", "Miller K", "Miller L",
                "Asymmetry angle [deg]", "Azimuthal angle [deg]",
                "Inclination angle [deg]", "Dump to file", "File name"]

    def unitFlags(self):
        return ["True",          "True",         "True",           "True",     "True",     "True",
                "True",                  "True",
                "True",                    "True",         "self.DUMP_TO_FILE == 0"]

    def compute(self):

        if not self._input_available:
            raise Exception("CrystalPassive: Input data not available!\n")

        # Translate CRYSTAL_TYPE (int) into a crystal name (string).
        CRYSTAL_NAME = self.crystal_names[self.CRYSTAL_NAME]

        outgoing_bunch = OWCrystalPassive.calculate_external_CrystalPassive(GEOMETRY_TYPE=self.GEOMETRY_TYPE,
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
        # if fileName == None:
        #     print("No file to send")
        # else:
        #     self.send("oasyscrystalpy-file",fileName)
        self.send("photon bunch", outgoing_bunch)
        print("CrystalPassive: The results were sent to the viewer.\n")

    def defaults(self):
        self.resetSettings()
        self.compute()
        return

    def get_doc(self):
        print("CrystalPassive: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'CrystalActive'+'.txt')
        print("CrystalPassive: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("CrystalPassive: sys.platform did not yield an acceptable value!\n")
        os.system(command)

    @staticmethod
    def calculate_external_CrystalPassive(GEOMETRY_TYPE,
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
            raise Exception("CrystalPassive: The geometry type could not be interpreted!\n")

        # Create a diffraction setup.
        # At this stage I translate angles in radians, energy in eV and all other values in SI units.
        print("CrystalPassive: Creating a diffraction setup...\n")

        diffraction_setup = DiffractionSetup(geometry_type=GEOMETRY_TYPE_OBJECT,  # GeometryType object
                                             crystal_name=str(CRYSTAL_NAME),  # string
                                             thickness=float(THICKNESS) * 1e-2,  # meters
                                             miller_h=int(MILLER_H),  # int
                                             miller_k=int(MILLER_K),  # int
                                             miller_l=int(MILLER_L),  # int
                                             asymmetry_angle=float(ASYMMETRY_ANGLE) / 180 * np.pi,  # radians
                                             azimuthal_angle=float(AZIMUTHAL_ANGLE) / 180 * np.pi,  # radians
                                             incoming_photons=incoming_bunch)

        # Create a Diffraction object.
        diffraction = Diffraction()

        # Create a PhotonBunch object holding the results of the diffraction calculations.
        print("CrystalPassive: Calculating the outgoing photons...\n")
        outgoing_bunch = diffraction.calculateDiffractedPhotonBunch(diffraction_setup, INCLINATION_ANGLE)

        # Check that the result of the calculation is indeed a PhotonBunch object.
        if not isinstance(outgoing_bunch, PhotonBunch):
            raise Exception("CrystalPassive: Expected PhotonBunch as a result, found {}!\n".format(type(outgoing_bunch)))

        # Dump data to file if requested.
        if DUMP_TO_FILE == 0:

            print("CrystalPassive: Writing data in {file}...\n".format(file=FILE_NAME))

            with open(FILE_NAME, "w") as file:
                try:
                    # file.write("VALUES:\n\n"
                    #            "geometry type: {geometry_type}\n"
                    #            "crystal name: {crystal_name}\n"
                    #            "thickness: {thickness}\n"
                    #            "miller H: {miller_h}\n"
                    #            "miller K: {miller_k}\n"
                    #            "miller L: {miller_l}\n"
                    #            "asymmetry angle: {asymmetry_angle}\n"
                    #            "azimuthal angle: {azimuthal_angle}\n"
                    #            "inclination angle: {inclination_angle}\n\n".format(
                    #                     geometry_type=GEOMETRY_TYPE_OBJECT.description(),
                    #                     crystal_name=CRYSTAL_NAME,
                    #                     thickness=THICKNESS,
                    #                     miller_h=MILLER_H,
                    #                     miller_k=MILLER_K,
                    #                     miller_l=MILLER_L,
                    #                     asymmetry_angle=ASYMMETRY_ANGLE,
                    #                     azimuthal_angle=AZIMUTHAL_ANGLE,
                    #                     inclination_angle=INCLINATION_ANGLE))
                    # file.write("INCOMING PHOTONS:\n\n")
                    # file.write(incoming_bunch.to_string())
                    # file.write("OUTGOING PHOTONS:\n\n")
                    # file.write(outgoing_bunch.to_string())
                    file.write("#S 1 photon bunch\n"
                               "#N 8\n"
                               "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3\n")
                    file.write(outgoing_bunch.to_string())

                except:
                    raise Exception("CrystalPassive: The data could not be dumped onto the specified file!\n")

        return outgoing_bunch


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWCrystalPassive()
    w.show()
    app.exec()
    w.saveSettings()
