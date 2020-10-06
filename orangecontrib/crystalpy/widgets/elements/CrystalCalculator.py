import numpy as np
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources
import sys
import os
from crystalpy.diffraction.DiffractionSetupSweeps import DiffractionSetupSweeps
from crystalpy.diffraction.Diffraction import Diffraction
from crystalpy.diffraction.GeometryType import BraggDiffraction, BraggTransmission, LaueDiffraction, LaueTransmission
from crystalpy.polarization.MuellerDiffraction import MuellerDiffraction
from crystalpy.util.StokesVector import StokesVector
from orangecontrib.crystalpy.util.MailingBox import MailingBox


class OWCrystalCalculator(widget.OWWidget):
    name = "Crystal Calculator"
    id = "orange.widgets.dataCrystalCalculator"
    description = "Compute the diffracted intensities and polarization from a crystal."
    icon = "icons/CrystalCalculator.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 50
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "CrystalCalculator"]
    outputs = [{"name": "diffraction data",
                "type": MailingBox,
                "doc": "transfer diffraction results"},
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
    ENERGY_POINTS = Setting(1)  # int
    ENERGY = Setting(8000)  # eV
    ENERGY_MIN = Setting(8000)  # eV
    ENERGY_MAX = Setting(8000)  # eV
    ANGLE_DEVIATION_POINTS = Setting(200)  # int
    ANGLE_DEVIATION = Setting(0)  # microradians
    ANGLE_DEVIATION_MIN = Setting(-100)  # microradians
    ANGLE_DEVIATION_MAX = Setting(100)  # microradians
    STOKES_S0 = Setting(1.0)
    STOKES_S1 = Setting(1.0)
    STOKES_S2 = Setting(0.0)
    STOKES_S3 = Setting(0.0)
    INCLINATION_ANGLE = Setting(45.0)  # degrees
    DUMP_TO_FILE = Setting(1)  # Yes
    FILE_NAME = "crystal_calculator.dat"

    def __init__(self):
        super().__init__()

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
        gui.lineEdit(box1, self, "ENERGY_POINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ENERGY",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 10
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ENERGY_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)
        
        # widget index 11
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ENERGY_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 12
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_POINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 13
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ANGLE_DEVIATION",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=int,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 14
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_MIN",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1) 
        
        # widget index 15
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ANGLE_DEVIATION_MAX",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 16
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S0",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 17
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S1",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 18
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S2",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 19
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "STOKES_S3",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 20
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "INCLINATION_ANGLE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 21
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["No", "Yes"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)
        
        # widget index 22
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        print("CrystalCalculator: Crystal calculator initialized.\n")

        gui.rubber(self.controlArea)

    def unitLabels(self):
        return ["Geometry type", "Crystal name", "Thickness [cm]", "Miller H", "Miller K", "Miller L",
                "Asymmetry angle [deg]", "Azimuthal angle [deg]",
                "Energy points", "Energy [eV]",             "Minimum energy [eV]",     "Maximum energy [eV]",
                "Angular deviation points", "Angle deviation [urad]",           "Minimum angular deviation [urad]", "Maximum angular deviation [urad]",
                "Stokes parameter S0", "Stokes parameter S1", "Stokes parameter S2", "Stokes parameter S3",
                "Inclination angle [deg]", "Dump to file", "File name"]

    def unitFlags(self):
        return ["True",          "True",         "True",           "True",     "True",     "True",
                "True",                  "True",
                "True",          "self.ENERGY_POINTS == 1", "self.ENERGY_POINTS != 1", "self.ENERGY_POINTS != 1",
                "True",                     "self.ANGLE_DEVIATION_POINTS == 1", "self.ANGLE_DEVIATION_POINTS != 1", "self.ANGLE_DEVIATION_POINTS != 1",
                "True",                "True",                "True",                "True",
                "True",                    "True",          "self.DUMP_TO_FILE == 1"]

    def compute(self):

        # Translate CRYSTAL_TYPE (int) into a crystal name (string).
        CRYSTAL_NAME = self.crystal_names[self.CRYSTAL_NAME]

        if self.ENERGY_POINTS == 1:
            self.ENERGY_MIN = self.ENERGY_MAX = self.ENERGY

        if self.ANGLE_DEVIATION_POINTS == 1:
            self.ANGLE_DEVIATION_MIN = self.ANGLE_DEVIATION_MAX = self.ANGLE_DEVIATION

        plot_data = OWCrystalCalculator.calculate_external_CrystalCalculator(GEOMETRY_TYPE=self.GEOMETRY_TYPE,
                                                                     CRYSTAL_NAME=CRYSTAL_NAME,
                                                                     THICKNESS=self.THICKNESS,
                                                                     MILLER_H=self.MILLER_H,
                                                                     MILLER_K=self.MILLER_K,
                                                                     MILLER_L=self.MILLER_L,
                                                                     ASYMMETRY_ANGLE=self.ASYMMETRY_ANGLE,
                                                                     AZIMUTHAL_ANGLE=self.AZIMUTHAL_ANGLE,
                                                                     ENERGY_POINTS=self.ENERGY_POINTS,
                                                                     ENERGY_MIN=self.ENERGY_MIN,
                                                                     ENERGY_MAX=self.ENERGY_MAX,
                                                                     ANGLE_DEVIATION_POINTS=self.ANGLE_DEVIATION_POINTS,
                                                                     ANGLE_DEVIATION_MIN=self.ANGLE_DEVIATION_MIN,
                                                                     ANGLE_DEVIATION_MAX=self.ANGLE_DEVIATION_MAX,
                                                                     STOKES_S0=self.STOKES_S0,
                                                                     STOKES_S1=self.STOKES_S1,
                                                                     STOKES_S2=self.STOKES_S2,
                                                                     STOKES_S3=self.STOKES_S3,
                                                                     INCLINATION_ANGLE=self.INCLINATION_ANGLE,
                                                                     DUMP_TO_FILE=self.DUMP_TO_FILE,
                                                                     FILE_NAME=self.FILE_NAME)
        self.send("diffraction data", plot_data)
        print("CrystalCalculator: The results were sent to the viewer.\n")

    def defaults(self):
        self.resetSettings()
        self.compute()
        return

    def get_doc(self):
        print("CrystalCalculator: help pressed.")
        home_doc = resources.package_dirname("orangecontrib.crystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'CrystalCalculator'+'.txt')
        print("CrystalCalculator: Opening file %s" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("CrystalCalculator: sys.platform did not yield an acceptable value!")
        os.system(command)

    @staticmethod
    def calculate_external_CrystalCalculator(GEOMETRY_TYPE,
                                         CRYSTAL_NAME,
                                         THICKNESS,
                                         MILLER_H,
                                         MILLER_K,
                                         MILLER_L,
                                         ASYMMETRY_ANGLE,
                                         AZIMUTHAL_ANGLE,
                                         ENERGY_POINTS,
                                         ENERGY_MIN,
                                         ENERGY_MAX,
                                         ANGLE_DEVIATION_POINTS,
                                         ANGLE_DEVIATION_MIN,
                                         ANGLE_DEVIATION_MAX,
                                         STOKES_S0,
                                         STOKES_S1,
                                         STOKES_S2,
                                         STOKES_S3,
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
            raise Exception("CrystalCalculator: The geometry type could not be interpreted!")

        # Create a diffraction setup.
        # At this stage I translate angles in radians, energy in eV and all other values in SI units.
        print("CrystalCalculator: Creating a diffraction setup...\n")

        if ENERGY_POINTS == 1:
            if ENERGY_MIN != ENERGY_MAX:
                raise Exception("CrystalCalculator: Finite energy range with only one sampled value!")

        diffraction_setup = DiffractionSetupSweeps(geometry_type=GEOMETRY_TYPE_OBJECT,  # GeometryType object
                                                   crystal_name=str(CRYSTAL_NAME),  # string
                                                   thickness=float(THICKNESS) * 1e-2,  # meters
                                                   miller_h=int(MILLER_H),  # int
                                                   miller_k=int(MILLER_K),  # int
                                                   miller_l=int(MILLER_L),  # int
                                                   asymmetry_angle=float(ASYMMETRY_ANGLE) / 180 * np.pi,  # radians
                                                   azimuthal_angle=float(AZIMUTHAL_ANGLE) / 180 * np.pi,  # radians
                                                   energy_min=float(ENERGY_MIN),  # eV
                                                   energy_max=float(ENERGY_MAX),  # eV
                                                   energy_points=int(ENERGY_POINTS),  # int
                                                   angle_deviation_min=float(ANGLE_DEVIATION_MIN) * 1e-6,  # radians
                                                   angle_deviation_max=float(ANGLE_DEVIATION_MAX) * 1e-6,  # radians
                                                   angle_deviation_points=int(ANGLE_DEVIATION_POINTS))  # int

        # Create a Diffraction object.
        diffraction = Diffraction()

        # Create a DiffractionResult object holding the results of the diffraction calculations.
        print("CrystalCalculator: Calculating the diffraction results...\n")
        diffraction_result = diffraction.calculateDiffraction(diffraction_setup)

        # Create a StokesVector object.
        incoming_stokes_vector = StokesVector([STOKES_S0, STOKES_S1, STOKES_S2, STOKES_S3])

        # Create a MuellerDiffraction object.
        mueller_diffraction = MuellerDiffraction(diffraction_result,
                                                 incoming_stokes_vector,
                                                 float(INCLINATION_ANGLE) * np.pi / 180)

        # Create a MullerResult object.
        print("CrystalCalculator: Calculating the Stokes vector...\n")
        mueller_result = mueller_diffraction.calculate_stokes()

        # Create the data to output.
        output_data = MailingBox(diffraction_result, mueller_result)

        # Dump data to file if requested.
        if DUMP_TO_FILE == 1:

            print("CrystalCalculator: Writing data in {file}...\n".format(file=FILE_NAME))

            with open(FILE_NAME, "w") as file:
                try:
                    file.write("VALUES:\n\n"
                               "geometry type: {geometry_type}\n"
                               "crystal name: {crystal_name}\n"
                               "thickness: {thickness}\n"
                               "miller H: {miller_h}\n"
                               "miller K: {miller_k}\n"
                               "miller L: {miller_l}\n"
                               "asymmetry angle: {asymmetry_angle}\n"
                               "azimuthal angle: {azimuthal_angle}\n"
                               "energy points: {energy_points}\n"
                               "energy minimum: {energy_min}\n"
                               "energy maximum: {energy_max}\n"
                               "deviation angle points: {angle_deviation_points}\n"
                               "deviation angle minimum: {angle_deviation_min}\n"
                               "deviation angle maximum: {angle_deviation_max}\n"
                               "inclination angle: {inclination_angle}\n"
                               "incoming Stokes vector: {incoming_stokes_vector}\n\n"
                               "RESULTS:\n\n"
                               "S-Polarization:\n"
                               "Intensity: {s_intensity}\n"
                               "Phase: {s_phase}\n\n"
                               "P-Polarization:\n"
                               "Intensity: {p_intensity}\n"
                               "Phase: {p_phase}\n\n"
                               "SP-Difference:\n"
                               "Intensity: {sp_intensity}\n"
                               "Phase: {sp_phase}\n\n"
                               "Stokes vector:\n"
                               "S0: {s0}\n"
                               "S1: {s1}\n"
                               "S2: {s2}\n"
                               "S3: {s3}\n\n"
                               "Degree of circular polarization: {pol_degree}".format(
                                        geometry_type=GEOMETRY_TYPE_OBJECT.description(),
                                        crystal_name=CRYSTAL_NAME,
                                        thickness=THICKNESS,
                                        miller_h=MILLER_H,
                                        miller_k=MILLER_K,
                                        miller_l=MILLER_L,
                                        asymmetry_angle=ASYMMETRY_ANGLE,
                                        azimuthal_angle=AZIMUTHAL_ANGLE,
                                        energy_points=ENERGY_POINTS,
                                        energy_min=ENERGY_MIN,
                                        energy_max=ENERGY_MAX,
                                        angle_deviation_points=ANGLE_DEVIATION_POINTS,
                                        angle_deviation_min=ANGLE_DEVIATION_MIN,
                                        angle_deviation_max=ANGLE_DEVIATION_MAX,
                                        inclination_angle=INCLINATION_ANGLE,
                                        incoming_stokes_vector=incoming_stokes_vector.components(),
                                        s_intensity=diffraction_result.sIntensityByEnergy(ENERGY_MIN),
                                        s_phase=diffraction_result.sPhaseByEnergy(ENERGY_MIN, deg=True),
                                        p_intensity=diffraction_result.pIntensityByEnergy(ENERGY_MIN),
                                        p_phase=diffraction_result.pPhaseByEnergy(ENERGY_MIN, deg=True),
                                        sp_intensity=diffraction_result.differenceIntensityByEnergy(ENERGY_MIN),
                                        sp_phase=diffraction_result.differencePhaseByEnergy(ENERGY_MIN, deg=True),
                                        s0=mueller_result.s0_by_energy(ENERGY_MIN),
                                        s1=mueller_result.s1_by_energy(ENERGY_MIN),
                                        s2=mueller_result.s2_by_energy(ENERGY_MIN),
                                        s3=mueller_result.s3_by_energy(ENERGY_MIN),
                                        pol_degree=mueller_result.polarization_degree_by_energy(ENERGY_MIN)))
                    file.close()
                    print("File written to disk: %s"%FILE_NAME)
                except:
                    raise Exception("CrystalCalculator: The data could not be dumped onto the specified file!")

        return output_data


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWCrystalCalculator()
    w.show()
    app.exec()
    w.saveSettings()
