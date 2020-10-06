import numpy as np
import sys
import os
import xraylib

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources

from crystalpy.util.Vector import Vector
from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch

class OWAlignmentTool(widget.OWWidget):
    name = "AlignmentTool"
    id = "orange.widgets.dataAlignmentTool"
    description = "Interface between lab reference frame and crystal reference frame."
    icon = "icons/Alignment.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 20
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "AlignmentTool"]
    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "photons"},
               ]
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "handler": "_set_input",
               "doc": "photons"}]

    want_main_area = False

    BASE_ENERGY = Setting(8000.0)  # eV
    CRYSTAL_NAME = Setting(0)  # Si
    MILLER_H = Setting(1)  # int
    MILLER_K = Setting(1)  # int
    MILLER_L = Setting(1)  # int
    ALPHA_X = Setting(0.0)  # degrees
    MOA = Setting(0)  # 180 - > (+) position
    MODE = Setting(0)  # lab-to-crystal
    DUMP_TO_FILE = Setting(1)  # Yes
    FILE_NAME = Setting("alignment_tool.dat")

    def __init__(self):
        super().__init__()

        self._input_available = False

        # Define a tuple of crystals to choose from.
        self.crystal_names = ("Si", "Ge", "Diamond")

        print("AlignmentTool: Alignment tool initialized.\n")

        box0 = gui.widgetBox(self.controlArea, " ", orientation="horizontal")

        # widget buttons: generate, set defaults, help
        gui.button(box0, self, "Apply", callback=self.apply)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)

        box = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        idx = -1

        # widget index 0
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "BASE_ENERGY",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
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
        gui.lineEdit(box1, self, "MILLER_H",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 3
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "MILLER_K",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 4
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "MILLER_L",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 5
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ALPHA_X",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 6
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "MOA",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=['0', '180'],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 7
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "MODE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=['Ray-to-crystal', 'Crystal-to-ray'],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 8
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=['No', 'Yes'],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        gui.rubber(self.controlArea)

        # Load crystal from xraylib.
        self.CRYSTAL = xraylib.Crystal_GetCrystal(self.crystal_names[self.CRYSTAL_NAME])

    def _set_input(self, photon_bunch):
        if photon_bunch is not None:
            self._input_available = True
            self.incoming_bunch = photon_bunch
            self.apply()

    def unitLabels(self):
        return ["Base energy [eV]", "Crystal name", "Miller H", "Miller K", "Miller L",
                "Asymmetry angle [deg]", "Mirror orientation angle [deg] -not implemented-", "Mode",
                "Dump to file", "File name"]

    def unitFlags(self):
        return ["True",             "True",         "True",     "True",     "True",
                "True",            "True",                     "True",
                "True",         "self.DUMP_TO_FILE == 1"]

    def apply(self):

        if not self._input_available:
            raise Exception("AlignmentTool: Input data not available!\n")

        energy_in_kev = self.BASE_ENERGY / 1000.0

        outgoing_bunch = PolarizedPhotonBunch([])

        x_axis = Vector(1, 0, 0)
        neg_x_axis = Vector(-1, 0, 0)

        # Retrieve Bragg angle from xraylib.
        angle_bragg = xraylib.Bragg_angle(self.CRYSTAL,
                                          energy_in_kev,
                                          self.MILLER_H,
                                          self.MILLER_K,
                                          self.MILLER_L)

        # TODO: change rotation using the crystalpy tool to get full alignment.
        for i in range(self.incoming_bunch.getNumberOfPhotons()):
            polarized_photon = self.incoming_bunch.getPhotonIndex(i)

            if self.MODE == 0:  # ray-to-crystal
                rotated_vector = polarized_photon.unitDirectionVector().\
                    rotateAroundAxis(neg_x_axis, angle_bragg + self.ALPHA_X*np.pi/180)

            elif self.MODE == 1:  # crystal-to-ray
                rotated_vector = polarized_photon.unitDirectionVector(). \
                    rotateAroundAxis(neg_x_axis, angle_bragg - self.ALPHA_X*np.pi/180)

            else:
                raise Exception("AlignmentTool: The alignment mode could not be interpreted correctly!\n")

            polarized_photon.setUnitDirectionVector(rotated_vector)
            outgoing_bunch.addPhoton(polarized_photon)

        # Dump data to file if requested.
        if self.DUMP_TO_FILE:

            print("AlignmentTool: Writing data in {file}...\n".format(file=self.FILE_NAME))

            with open(self.FILE_NAME, "w") as file:
                try:
                    file.write("#S 1 photon bunch\n"
                               "#N 9\n"
                               "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3  CircularPolarizationDegree\n")
                    file.write(outgoing_bunch.toString())
                    file.close()
                    print("File written to disk: %s \n"%self.FILE_NAME)

                except:
                    raise Exception("AlignmentTool: The data could not be dumped onto the specified file!\n")

        self.send("photon bunch", outgoing_bunch)
        print("AlignmentTool: Photon bunch aligned.\n")

    def defaults(self):
        self.resetSettings()
        self.generate()
        return

    def get_doc(self):
        print("AlignmentTool: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.crystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'AlignmentTool'+'.txt')
        print("AlignmentTool: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("AlignmentTool: sys.platform did not yield an acceptable value!\n")
        os.system(command)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWAlignmentTool()
    w.show()
    app.exec()
    w.saveSettings()
