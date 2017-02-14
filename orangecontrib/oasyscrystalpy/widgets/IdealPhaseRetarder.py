import numpy as np
from PyQt4.QtGui import QIntValidator, QDoubleValidator, QApplication, QSizePolicy
# from PyMca5.PyMcaIO import specfilewrapper as specfile
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources
import sys, os

from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.polarization.MuellerMatrix import MuellerMatrix

class OWIdealPhaseRetarder(widget.OWWidget):
    name = "IdealPhaseRetarder"
    id = "orange.widgets.dataIdealPhaseRetarder"
    description = "Application to compute..."
    icon = "icons/IdealPhaseRetarder.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.fr"
    priority = 10
    category = ""
    keywords = ["oasyscrystalpy", "IdealPhaseRetarder"]
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "handler": "_set_input_photon_bunch",
               "doc": ""},
              ]

    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "transfer diffraction results"},
               ]

    # widget input (if needed)
    # inputs = [{"name": "Name",
    #            "type": type,
    #            "handler": None,
    #            "doc": ""}]

    want_main_area = False

    TYPE = Setting(0)
    THETA = Setting(0.0)
    DELTA = Setting(0.0)


    def __init__(self):
        super().__init__()

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.calculate_IdealPhaseRetarder)
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
                     items=['general', 'Quarter Wave Plate (fast-axis horizontal)', 'Quarter Wave Plate (fast-axis vertical)', 'Half Wave Plate (also Ideal Mirror)'],
                     valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "THETA",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "DELTA",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ["Type", "angle of the fast axis theta [deg]","phase difference between the fast and slow axes delta [deg]"]


    def unitFlags(self):
         return ["True", "self.TYPE == 0", "self.TYPE == 0"]


    def defaults(self):
         self.resetSettings()
         self.calculate_IdealPhaseRetarder()
         return

    def get_doc(self):
        print("help pressed.")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc,'IdealPhaseRetarder'+'.txt')
        print("Opening file %s"%filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        os.system(command)


    def _set_input_photon_bunch(self, photon_bunch):
        if photon_bunch is not None:
            print("<><> IdealPhaseRetarder has received PolarizedPhotonBunch)")
            self._input_available = True
            self.incoming_bunch = photon_bunch

    def calculate_IdealPhaseRetarder(self):
        print("Inside calculate_IdealPhaseRetarder. ")

        if self._input_available:
            photon_bunch = self.incoming_bunch
            if self.TYPE == 0:
                mm = MuellerMatrix.initialize_as_general_linear_retarder(
                    theta=self.THETA*np.pi/180,delta=self.DELTA*np.pi/180)
            elif self.TYPE == 1:
                mm = MuellerMatrix.initialize_as_quarter_wave_plate_fast_horizontal()
            elif self.TYPE == 2:
                mm = MuellerMatrix.initialize_as_quarter_wave_plate_fast_vertical()
            elif self.TYPE == 3:
                mm = MuellerMatrix.initialize_as_half_wave_plate()


            for index, polarized_photon in enumerate(photon_bunch):
                polarized_photon.applyMuellerMatrix(mm)

            self.send("photon bunch", photon_bunch)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWIdealPhaseRetarder()
    w.show()
    app.exec()
    w.saveSettings()
