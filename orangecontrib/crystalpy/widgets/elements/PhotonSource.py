import numpy as np
import sys
import os

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources

from crystalpy.util.StokesVector import StokesVector
from crystalpy.util.Vector import Vector
from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.util.PolarizedPhoton import PolarizedPhoton


class OWPhotonSource(widget.OWWidget):
    name = "PhotonSource"
    id = "orange.widgets.dataPhotonSource"
    description = "Application to generate photon bunches"
    icon = "icons/LightBulb.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 10
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "PhotonSource"]
    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "emitted photons"},]


    want_main_area = False

    ENERGY_POINTS = Setting(1)  # int
    ENERGY_MIN = Setting(8000)  # eV
    ENERGY_MAX = Setting(8000)  # eV
    ENERGY = Setting(8000)  # eV
    ANGLE_DEVIATION_POINTS = Setting(200)  # int
    ANGLE_DEVIATION_MIN = Setting(-100)  # microradians
    ANGLE_DEVIATION_MAX = Setting(100)  # microradians
    ANGLE_DEVIATION = Setting(0)
    STOKES_S0 = Setting(1.0)
    STOKES_S1 = Setting(1.0)
    STOKES_S2 = Setting(0.0)
    STOKES_S3 = Setting(0.0)
    DUMP_TO_FILE = Setting(1)  # Yes
    FILE_NAME = Setting("photon_source.dat")

    def __init__(self):
        super().__init__()

        box0 = gui.widgetBox(self.controlArea, " ", orientation="horizontal")
        # widget buttons: generate, set defaults, help
        gui.button(box0, self, "Generate", callback=self.generate)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)

        box = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        idx = -1

        # widget index 0
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ENERGY_POINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 1
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ENERGY_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 2
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ENERGY_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 3
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ENERGY",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 4
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_POINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 5
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 6
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 7
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 8
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S0",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S1",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 10
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S2",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 11
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S3",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 12
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["No", "Yes"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 13
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        print("PhotonSource: Photon source initialized.\n")

        gui.rubber(self.controlArea)

    def unitLabels(self):
        return ["Energy points", "Minimum energy [eV]",     "Maximum energy [eV]",     "Energy",
                "Angular deviation points", "Minimum angular deviation [urad]", "Maximum angular deviation [urad]", "Angular deviation",
                "Stokes parameter S0", "Stokes parameter S1", "Stokes parameter S2", "Stokes parameter S3",
                "Dump to file", "File name"]

    def unitFlags(self):
        return ["True",          "self.ENERGY_POINTS != 1", "self.ENERGY_POINTS != 1", "self.ENERGY_POINTS == 1",
                "True",                     "self.ANGLE_DEVIATION_POINTS != 1", "self.ANGLE_DEVIATION_POINTS != 1", "self.ANGLE_DEVIATION_POINTS == 1",
                "True",                "True",                "True",                "True",
                "True",         "self.DUMP_TO_FILE == 1"]

    def generate(self):

        if self.ENERGY_POINTS == 1:
            # monochromatic bunch.
            self.ENERGY_MIN = self.ENERGY_MAX = self.ENERGY

        energies = np.linspace(self.ENERGY_MIN,
                               self.ENERGY_MAX,
                               self.ENERGY_POINTS)

        if self.ANGLE_DEVIATION_POINTS == 1:
            # unidirectional bunch.
            ANGLE_DEVIATION_MIN = ANGLE_DEVIATION_MAX = self.ANGLE_DEVIATION * 1e-6  # urad

        else:
            ANGLE_DEVIATION_MIN = self.ANGLE_DEVIATION_MIN * 1e-6  # urad
            ANGLE_DEVIATION_MAX = self.ANGLE_DEVIATION_MAX * 1e-6  # urad

        deviations = np.linspace(ANGLE_DEVIATION_MIN,
                                 ANGLE_DEVIATION_MAX,
                                 self.ANGLE_DEVIATION_POINTS)

        stokes_vector = StokesVector([self.STOKES_S0,
                                      self.STOKES_S1,
                                      self.STOKES_S2,
                                      self.STOKES_S3])

        # Following XOP conventions, the photon bunch travels along the y axis in the lab frame of reference.
        base_direction = Vector(0, 1, 0)
        # TODO: check this sign and possibly change it.
        # Setting (-1,0,0) means that negative deviation correspond to positive vz and after rotation
        # to match the crystal correspond to theta_bragg -  delta, so deviation has the same sign of delta

        rotation_axis = Vector(-1, 0, 0)

        # To match the deviation sign conventions with those adopted in the crystal diffraction part,
        # I have to define a positive deviation as a clockwise rotation from the y axis,
        # and consequently a negative deviation as a counterclockwise rotation from the y axis.

        polarized_photons = list()
        for energy in energies:
            for deviation in deviations:
                direction = base_direction.rotateAroundAxis(rotation_axis, deviation)
                incoming_photon = PolarizedPhoton(energy, direction, stokes_vector)
                polarized_photons.append(incoming_photon)

        photon_bunch = PolarizedPhotonBunch(polarized_photons)

        # Dump data to file if requested.
        if self.DUMP_TO_FILE:

            print("PhotonSource: Writing data in {file}...\n".format(file=self.FILE_NAME))

            with open(self.FILE_NAME, "w") as file:
                try:
                    file.write("#S 1 photon bunch\n"
                               "#N 9\n"
                               "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3  CircularPolarizationDregree\n")
                    file.write(photon_bunch.toString())
                    file.close()
                    print("File written to disk: %s \n"%self.FILE_NAME)
                except:
                    raise Exception("PhotonSource: The data could not be dumped onto the specified file!\n")

        self.send("photon bunch", photon_bunch)
        print("PhotonSource: Photon bunch generated.\n")

    def defaults(self):
        self.resetSettings()
        self.generate()
        return

    def get_doc(self):
        print("PhotonSource: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.crystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'PhotonSource'+'.txt')
        print("PhotonSource: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("PhotonSource: sys.platform did not yield an acceptable value!\n")
        os.system(command)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWPhotonSource()
    w.show()
    app.exec()
    w.saveSettings()
