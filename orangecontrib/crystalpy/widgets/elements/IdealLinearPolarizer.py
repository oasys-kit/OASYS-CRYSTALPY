import numpy as np
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
    priority = 30
    category = ""
    keywords = ["IdealLinearPolarizer"]
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
    DUMP_TO_FILE = Setting(1)
    FILE_NAME = Setting("linear_polarizer.dat")

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
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1) 

        # widget index 2
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["No","Yes"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 3
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ["Type", "angle of the polarizer theta [deg]", "Dump to file", "File name"]


    def unitFlags(self):
         return ["True", "self.TYPE == 0","True","self.DUMP_TO_FILE == 1"]


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


    def _set_input_photon_bunch(self, photon_bunch):
        self._input_available = False
        if photon_bunch is not None:
            self._input_available = True
            self.incoming_bunch = photon_bunch
            self.calculate_IdealLinearPolarizer()



    def calculate_IdealLinearPolarizer(self):

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

            photon_bunch_out = PolarizedPhotonBunch()


            for index in range(photon_bunch.getNumberOfPhotons()):
                polarized_photon = photon_bunch.getPhotonIndex(index)

                polarized_photon.applyMuellerMatrix(mm)

                photon_bunch_out.addPhoton(polarized_photon)


            self.send("photon bunch", photon_bunch_out)

            # Dump data to file if requested.
            if self.DUMP_TO_FILE == 1:

                print("CrystalPassive: Writing data in {file}...\n".format(file=self.FILE_NAME))

                with open(self.FILE_NAME, "w") as file:
                    try:
                        file.write("#S 1 photon bunch\n"
                                   "#N 9\n"
                                   "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3  circular polarization\n")
                        file.write(photon_bunch_out.toString())
                        file.close()
                        print("File written to disk: %s"%self.FILE_NAME)
                    except:
                        raise Exception("IdealLinerPolarizer: The data could not be dumped onto the specified file!\n")


        else:
            raise Exception("No photon beam available")



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWIdealLinearPolarizer()
    w.show()
    app.exec()
    w.saveSettings()
