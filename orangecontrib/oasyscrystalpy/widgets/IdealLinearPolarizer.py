import numpy as np
from PyQt4.QtGui import QIntValidator, QDoubleValidator, QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources
import sys, os

from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.polarization.MuellerMatrix import MuellerMatrix

class OWIdealLinearPolarizer(widget.OWWidget):
    name = "IdealLinearPolarizer"
    id = "orange.widgets.dataIdealLinearPolarizer"
    description = "Application to compute..."
    icon = "icons/IdealLinearPolarizer.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.fr"
    priority = 10
    category = ""
    keywords = ["oasyscrystalpy", "IdealLinearPolarizer"]
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "handler": "_set_input_photon_bunch",
               "doc": ""},
              ]

    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "transfer diffraction results"},
               ]

    want_main_area = False

    TYPE = Setting(0)
    THETA = Setting(0.0)


    def __init__(self):
        super().__init__()

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.calculate_IdealLinearPolarizer)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)
        self.process_showers()
        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") 
        
        
        idx = -1 
        
        # widget index 0 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "TYPE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=['general', 'Liner polarizer (horizontal transmission)', 'Liner polarizer (vertical transmission)', 'Liner polarizer (+45 deg transmission)', 'Liner polarizer (-45 deg transmission)'],
                     valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "THETA",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ["Type", "angle of the polarizer theta [deg]"]


    def unitFlags(self):
         return ["True", "self.TYPE == 0"]


    def defaults(self):
         self.resetSettings()
         self.calculate_IdealLinearPolarizer()
         return

    def get_doc(self):
        print("help pressed.")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc,'IdealLinearPolarizer'+'.txt')
        print("Opening file %s"%filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        os.system(command)

    #
    # this is the calculation method to be implemented by the user
    # It is defined as static method to get all inputs from the arguments so it
    # can easily moved outside the class
    #

    def _set_input_photon_bunch(self, photon_bunch):
        if photon_bunch is not None:
            self._input_available = True
            self.incoming_bunch = photon_bunch

    def calculate_IdealLinearPolarizer(self):
        print("Inside calculate_IdealLinearPolarizer. ")
        if self._input_available:
            # TYPE=self.TYPE,THETA=self.THETA,DELTA=self.DELTA
            photon_bunch = self.incoming_bunch
            if self.TYPE == 0:
                mm = MuellerMatrix.initialize_as_general_linear_polarizer(theta=self.THETA*np.pi/180)
            elif self.TYPE == 1:
                mm = MuellerMatrix.initialize_as_linear_polarizer_horizontal()
            elif self.TYPE == 2:
                mm = MuellerMatrix.initialize_as_linear_polarizer_vertical()
            elif self.TYPE == 3:
                mm = MuellerMatrix.initialize_as_linear_polarizer_plus45()
            elif self.TYPE == 4:
                mm = MuellerMatrix.initialize_as_linear_polarizer_minus45()

            print(mm.matrix)

            # for index, polarized_photon in enumerate(photon_bunch):
            #     print("before",polarized_photon.stokesVector().to_string())
            #     polarized_photon.applyMuellerMatrix(mm)
            #     print("after",polarized_photon.stokesVector().to_string())

            for index in range(len(photon_bunch)):
                polarized_photon = photon_bunch.get_photon_index(index)
                print(type(photon_bunch[index]))
                print("before",index,polarized_photon.stokesVector().to_string())

                polarized_photon.applyMuellerMatrix(mm)
                print("  after",polarized_photon.stokesVector().to_string())
                photon_bunch.set_photon_index(index,polarized_photon)

                polarized_photon2 = photon_bunch.get_photon_index(index)
                print("  after2",polarized_photon2.stokesVector().to_string())
            self.incoming_bunch = photon_bunch
            self.send("photon bunch", photon_bunch)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWIdealLinearPolarizer()
    w.show()
    app.exec()
    w.saveSettings()
