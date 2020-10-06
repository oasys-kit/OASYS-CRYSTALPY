# External libraries.
import numpy as np
import scipy.special
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import sys
import os

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget
import orangecanvas.resources as resources

# Project libraries.
from crystalpy.util.StokesVector import StokesVector
from crystalpy.util.Vector import Vector
from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.util.PolarizedPhoton import PolarizedPhoton

#############################################################################################
# srxraylib is a Python library by Manuel Sanchez del Rio (srio@esrf.fr)                    #
# which simulates the emission of radiation from BMs and IDs in a synchrotron storage ring. #
#                                                                                           #
# The function srfunc.sync_ang together with the function sync_f in this library compute    #
# the power density in Watts/mrad of the radiation emitted by a bending magnet.             #
#                                                                                           #
# The calculations are based on the formulae derived by Sokolov and Ternov in 1968 and      #
# later adapted by Green in 1976.                                                           #
#                                                                                           #
# References:                                                                               #
#       G K Green, "Spectra and optics of synchrotron radiation"                            #
#           BNL 50522 report (1976)                                                         #
#       A A Sokolov and I M Ternov, Synchrotron Radiation,                                  #
#           Akademik-Verlag, Berlin, 1968                                                   #
#       J D Jackson, Classical Electrodynamics,                                             #
#           John Wiley & Sons, New York, 1975                                               #
#############################################################################################

from srxraylib.sources.srfunc import sync_ang

# Import the constants needed for the computations.
try:
    import scipy.constants.codata

    codata = scipy.constants.codata.physical_constants

    codata_c, tmp1, tmp2 = codata["speed of light in vacuum"]
    codata_c = np.array(codata_c)

    codata_mee, tmp1, tmp2 = codata["electron mass energy equivalent in MeV"]
    codata_mee = np.array(codata_mee)

    codata_me, tmp1, tmp2 = codata["electron mass"]
    codata_me = np.array(codata_me)

    codata_h, tmp1, tmp2 = codata["Planck constant"]
    codata_h = np.array(codata_h)

    codata_ec, tmp1, tmp2 = codata["elementary charge"]
    codata_ec = np.array(codata_ec)

except ImportError:

    print("BendingMagnet: Failed to import scipy. Finding alternative ways.\n")

    codata_c = np.array(299792458.0)
    codata_mee = np.array(9.10938291e-31)
    codata_me = np.array(0.510999)
    codata_h = np.array(6.62606957e-34)
    codata_ec = np.array(1.602176565e-19)

m2ev = codata_c*codata_h/codata_ec  # wavelength(m) = m2ev / energy(eV).


def modified_sync_f(rAngle, rEnergy, polarization):
    """
    This is the same function as sync_f in srxraylib by Manuel Sanchez del Rio
    but accepts as inputs polarization = -1 and = 1, corresponding to RCP and LCP
    and assigns the Sokolov parameters l2 and l3 consequently.
    :param rAngle: the reduced angle, i.e., angle[rads]*Gamma. It can be a scalar or a vector.
    :type rAngle: numpy.ndarray
    :param rEnergy: a value for the reduced photon energy, i.e.,
                    energy/critical_energy. Scalar.
    :type rEnergy; float
    :param polarization: -1(LCP), 1(RCP), 2(sigma), 3(pi).
    :type polarization: int
    :rtype: numpy.ndarray
    """
    rAngle = np.array(rAngle)
    rEnergy = float(rEnergy)

    # note that for Sokolov-Ternov LCP has l2=l3=1/sqrt(2) and RCP has  l2=1/sqrt(2) and l3 = -1/sqrt(2)
    # they use a system where magnetic field is pointing up and the electron is rotating ccw

    # we use an electron rotating cw so the l3 are reversed


    if polarization == -1:  # LCP
        l2 = 1 / np.sqrt(2)
        l3 = l2

    elif polarization == 1:  # RCP
        l2 = 1 / np.sqrt(2)
        l3 = - l2

    elif polarization == 2:  # sigma
        l2 = 1.0
        l3 = 0.0

    elif polarization == 3:  # pi
        l2 = 0.0
        l3 = 1.0

    else:
        raise Exception("BendingMagnet.modified_sync_f: "
                        "the 'polarization' input is not within the set of allowed values!\n")
    #
    # Formula 11 in Green, pag.6
    #
    ji = np.sqrt(np.power(1.0 + np.power(rAngle, 2), 3))
    ji = np.outer(ji, rEnergy / 2.0)
    rAngle2 = np.outer(rAngle, (rEnergy * 0.0 + 1.0))
    efe = l2 * scipy.special.kv(2.0 / 3.0, ji) + \
        l3 * rAngle2 * scipy.special.kv(1.0 / 3.0, ji) / \
        np.sqrt(1.0 + np.power(rAngle2, 2))
    efe *= (1.0 + np.power(rAngle2, 2))
    efe *= efe

    return np.array(efe)


def stokes_calculator(energy, deviations, e_gev=6.04, i_a=0.2, hdiv_mrad=1.0, ec_ev=19551.88):
    """
    Calculates the Stokes vectors for each PolarizedPhoton according to the theory of the BM emission.
    It does this by use of a modified version of the sync_ang function that allows the computation of the
    power densities for the RCP and LCP components on top of the linear components.
    The dW_+1 and dW_-1 values are obtained by setting respectively:

        l2 = l3 = 1/sqrt(2) for RCP and
        l2 = -l3 = 1/sqrt(2) for LCP.

    The computation of dW_-1 (LCP), dW_1 (RCP), dW_2 (sigma) and dW_3 (pi) makes it possible to use
    the formula 3.23 from Sokolov & Ternov for the phase difference delta = phi_3 - phi_2.
    This in turn lead to the Stokes parameters as defined in Jackson, 7.27.

    The default values for the parameters are the typical ESRF values.
    :param energy: desired photon energy in eV.
    :type energy: float
    :param deviations: array of angle deviations in milliradians.
    :type deviations: numpy.ndarray
    :param e_gev: energy of the electrons in GeV.
    :type e_gev: float
    :param i_a: beam current in A.
    :type i_a: float
    :param hdiv_mrad: horizontal divergence of the beam in milliradians.
    :type hdiv_mrad; float
    :param ec_ev: critical energy as in Green, pag.3.
    :type ec_ev: float
    :return: list of StokesVector objects.
    :rtype: PolarizedPhotonBunch
    """
    #
    # Calculate some parameters needed by sync_f (copied from sync_ang by Manuel Sanchez del Rio).
    # a8 = 1.3264d13
    #
    deviations = np.array(deviations)
    a8 = codata_ec / np.power(codata_mee, 2) / codata_h * (9e-2 / 2 / np.pi)
    energy = float(energy)
    eene = energy / ec_ev
    gamma = e_gev * 1e3 / codata_mee

    #
    # Calculate the power densities for the 4 cases:
    #
    #    -1 --> left circularly polarized       l2 = -l3 = 1/sqrt(2)
    #     1 --> right circularly polarized      l2 = l3 = 1/sqrt(2)
    #     2 --> linear sigma component          l2 = 1 & l3 = 0
    #     3 --> linear pi component             l3 = 1 & l2 = 0
    #
    left_circular = modified_sync_f(deviations * gamma / 1e3, eene, polarization=-1) * \
        np.power(eene, 2) * \
        a8 * i_a * hdiv_mrad * np.power(e_gev, 2)  # -1

    right_circular = modified_sync_f(deviations * gamma / 1e3, eene, polarization=1) * \
        np.power(eene, 2) * \
        a8 * i_a * hdiv_mrad * np.power(e_gev, 2)  # 1

    sigma_linear = modified_sync_f(deviations * gamma / 1e3, eene, polarization=2) * \
        np.power(eene, 2) * \
        a8 * i_a * hdiv_mrad * np.power(e_gev, 2)  # 2

    pi_linear = modified_sync_f(deviations * gamma / 1e3, eene, polarization=3) * \
        np.power(eene, 2) * \
        a8 * i_a * hdiv_mrad * np.power(e_gev, 2)  # 3

    #
    # Calculate the phase difference delta according to Sokolov, formula 3.23.
    #
    delta = (left_circular - right_circular) / \
        (2 * np.sqrt(sigma_linear * pi_linear))

    delta = np.arcsin(delta)

    #
    # Calculate the Stokes parameters.
    #
    s_0 = sigma_linear + pi_linear
    s_1 = sigma_linear - pi_linear
    s_2 = np.sqrt(sigma_linear) * np.sqrt(pi_linear) * np.cos(delta)
    s_3 = np.sqrt(sigma_linear) * np.sqrt(pi_linear) * np.sin(delta)
    s_2 *= 2  # TODO: try to understand why if I multiply by 2 in the line above I get a warning.
    s_3 *= 2

    #
    # Normalize the Stokes parameters.
    #
    # modulus = np.sqrt(s_0 ** 2 + s_1 ** 2 + s_2 ** 2 + s_3 ** 2)
    #
    # if np.any(modulus != 0):
    #     s_0 /= modulus
    #     s_1 /= modulus
    #     s_2 /= modulus
    #     s_3 /= modulus
    #
    # else:
    #     raise Exception("BendingMagnet.stokes_calculator: Stokes vector is null vector!\n")

    maximum = np.max(s_0)
    s_0 /= maximum
    s_1 /= maximum
    s_2 /= maximum
    s_3 /= maximum

    # Following XOP conventions, the photon bunch travels along the y axis in the lab frame of reference.
    base_direction = Vector(0, 1, 0)
    rotation_axis = Vector(1, 0, 0)

    #
    # Create the PolarizedPhotonBunch.
    #
    # To match the deviation sign conventions with those adopted in the crystal diffraction part,
    # I have to define a positive deviation as a clockwise rotation from the y axis,
    # and consequently a negative deviation as a counterclockwise rotation from the y axis.
    #
    polarized_photons = list()
    deviations = np.multiply(deviations, 1e-3)  # mrad --> rad

    for i in range(len(deviations)):
        stokes_vector = StokesVector([s_0[i], s_1[i], s_2[i], s_3[i]])
        direction = base_direction.rotateAroundAxis(rotation_axis, deviations[i])
        incoming_photon = PolarizedPhoton(energy, direction, stokes_vector)
        polarized_photons.append(incoming_photon)

    photon_bunch = PolarizedPhotonBunch(polarized_photons)

    return photon_bunch


class OWBendingMagnet(widget.OWWidget):
    name = "BendingMagnet"
    id = "orange.widgets.dataBendingMagnet"
    description = "Generates photon bunch objects according to the power density profile of a bending magnet"
    icon = "icons/BendingMagnet.png"
    author = "create_widget.py"
    maintainer_email = "cappelli@esrf.fr"
    priority = 15
    category = ""
    keywords = ["oasyscrystalpy", "crystalpy", "BendingMagnet"]
    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "emitted photons"},
               ]

    # widget input (if needed)
    # inputs = [{"name": "Name",
    #            "type": type,
    #            "handler": None,
    #            "doc": ""}]

    # want_main_area = False

    ENERGY_POINTS = Setting(1)  # int
    ENERGY_MIN = Setting(8000)  # eV
    ENERGY_MAX = Setting(8000)  # eV
    ENERGY = Setting(8000)  # eV
    ANGLE_DEVIATION_POINTS = Setting(200)  # int
    ANGLE_DEVIATION_MIN = Setting(-100)  # microradians
    ANGLE_DEVIATION_MAX = Setting(100)  # microradians
    ANGLE_DEVIATION = Setting(0)  # microradians
    DUMP_TO_FILE = Setting(1)  # Yes.dat")
    FILE_NAME = Setting("bending_magnet_source.dat")

    # Setting as default ESRF parameters.
    ELECTRON_ENERGY = Setting(6.0)  # the electron energy [in GeV]
    ELECTRON_CURRENT = Setting(0.2)  # the electron beam intensity [in A]
    HORIZONTAL_DIVERGENCE = Setting(1.0)  # the horizontal divergence [in mrad]
    MAGNETIC_RADIUS = Setting(25.0)  # the magnetic radius [in m]

    # Allowing for the plotting of the BM emission profiles.
    VIEW_EMISSION_PROFILE = Setting(0)  # Yes

    def __init__(self):
        super().__init__()

        self.figure_canvas = None
        self.fig = plt.figure()
        self.figure_canvas = FigureCanvas(self.fig)
        self.mainArea.layout().addWidget(self.figure_canvas)

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
        gui.lineEdit(box1, self, "ELECTRON_ENERGY",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 9
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "ELECTRON_CURRENT",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 10
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "HORIZONTAL_DIVERGENCE",
                     label=self.unitLabels()[idx], addSpace=True,
                     valueType=float,)
        self.show_at(self.unitFlags()[idx], box1)

        # widget index 11
        idx += 1
        box1 = gui.widgetBox(box)
        gui.lineEdit(box1, self, "MAGNETIC_RADIUS",
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

        # widget index 13
        idx += 1
        box1 = gui.widgetBox(box)
        gui.comboBox(box1, self, "VIEW_EMISSION_PROFILE",
                     label=self.unitLabels()[idx], addSpace=True,
                     items=["Yes", "No"],
                     orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)

        self.process_showers()

        print("BendingMagnet: Bending magnet initialized.\n")

        gui.rubber(self.controlArea)

    def unitLabels(self):
        return ["Energy points", "Minimum energy [eV]",     "Maximum energy [eV]",     "Energy",
                "Angular deviation points", "Minimum angular deviation [urad]", "Maximum angular deviation [urad]", "Angular deviation",
                "Electron energy [GeV]", "Electron current [A]", "Horizontal divergence [mrad]", "Magnetic radius [m]",
                "Dump to file", "File name",               "View emission profile"]

    def unitFlags(self):
        return ["True",          "self.ENERGY_POINTS != 1", "self.ENERGY_POINTS != 1", "self.ENERGY_POINTS == 1",
                "True",                     "self.ANGLE_DEVIATION_POINTS != 1", "self.ANGLE_DEVIATION_POINTS != 1", "self.ANGLE_DEVIATION_POINTS == 1",
                "True",                  "True",                 "True",                         "True",
                "True",         "self.DUMP_TO_FILE == 1",  "True"]

    def generate(self):

        if self.figure_canvas is not None:
            self.mainArea.layout().removeWidget(self.figure_canvas)

        #
        # Calculating the critical energy in eV following Green pag.3.
        #
        gamma = self.ELECTRON_ENERGY * 1e3 / codata_mee  # the electron energy is given in GeV.
        critical_wavelength = 4.0 * np.pi * self.MAGNETIC_RADIUS / 3.0 / np.power(gamma, 3)  # wavelength in m.
        ec_ev = m2ev / critical_wavelength  # critical energy in eV.

        #
        # Constructing the angle and energy grids.
        #
        if self.ENERGY_POINTS == 1:
            # monochromatic bunch.
            ENERGY_MIN = ENERGY_MAX = self.ENERGY

        else:
            ENERGY_MIN = self.ENERGY_MIN
            ENERGY_MAX = self.ENERGY_MAX

        energies = np.linspace(start=ENERGY_MIN,
                               stop=ENERGY_MAX,
                               num=self.ENERGY_POINTS)

        if self.ANGLE_DEVIATION_POINTS == 1:
            # unidirectional bunch.
            ANGLE_DEVIATION_MIN = ANGLE_DEVIATION_MAX = self.ANGLE_DEVIATION * 1e-6  # urad --> rad

        else:
            ANGLE_DEVIATION_MIN = self.ANGLE_DEVIATION_MIN * 1e-6  # urad --> rad
            ANGLE_DEVIATION_MAX = self.ANGLE_DEVIATION_MAX * 1e-6  # urad --> rad

        deviations = np.linspace(start=ANGLE_DEVIATION_MIN,
                                 stop=ANGLE_DEVIATION_MAX,
                                 num=self.ANGLE_DEVIATION_POINTS)

        sync_ang_deviations = np.multiply(deviations, 1e3)  # sync_ang takes as an input angles in mrad, not urad.
        photon_bunch = PolarizedPhotonBunch([])

        for energy in energies:

            photon_bunch_to_add = stokes_calculator(energy, sync_ang_deviations, self.ELECTRON_ENERGY,
                                                    self.ELECTRON_CURRENT, self.HORIZONTAL_DIVERGENCE, float(ec_ev))
            photon_bunch.addBunch(photon_bunch_to_add)

        #
        # Dump data to file if requested.
        #
        if self.DUMP_TO_FILE:

            print("BendingMagnet: Writing data in {file}...\n".format(file=self.FILE_NAME))

            with open(self.FILE_NAME, "w") as file:
                try:
                    file.write("#S 1 photon bunch\n"
                               "#N 9\n"
                               "#L  Energy [eV]  Vx  Vy  Vz  S0  S1  S2  S3\n")
                    file.write(photon_bunch.toString())
                    file.close()
                    print("File written to disk: %s"%self.FILE_NAME)
                except:
                    raise Exception("BendingMagnet: The data could not be dumped onto the specified file!\n")

        #
        # Plotting the emission profiles according to user input if requested.
        #
        if self.VIEW_EMISSION_PROFILE == 1:

            self.fig.clf()  # clear the current Figure.
            self.figure_canvas.draw()

        elif self.VIEW_EMISSION_PROFILE == 0:

            self.fig.clf()  # clear the current Figure.
            ax = self.fig.add_subplot(111)

            toptitle = "Bending Magnet angular emission"
            xtitle = "Psi[mrad]"
            ytitle = "Power density[Watts/mrad]"

            if self.ENERGY_POINTS == 1:
                flux = sync_ang(1, sync_ang_deviations, polarization=0,
                                e_gev=self.ELECTRON_ENERGY, i_a=self.ELECTRON_CURRENT,
                                hdiv_mrad=1.0, energy=self.ENERGY, ec_ev=ec_ev)

                ax.plot(sync_ang_deviations, flux, 'g', label="E={} keV".format(self.ENERGY * 1e-3))

            else:
                flux_Emin = sync_ang(1, sync_ang_deviations, polarization=0,  # energy = lower limit.
                                     e_gev=self.ELECTRON_ENERGY, i_a=self.ELECTRON_CURRENT,
                                     hdiv_mrad=1.0, energy=self.ENERGY_MIN, ec_ev=ec_ev)

                flux_Emax = sync_ang(1, sync_ang_deviations, polarization=0,  # energy = upper limit.
                                     e_gev=self.ELECTRON_ENERGY, i_a=self.ELECTRON_CURRENT,
                                     hdiv_mrad=1.0, energy=self.ENERGY_MAX, ec_ev=ec_ev)

                ax.plot(sync_ang_deviations, flux_Emin, 'r', label="E min={} keV".format(self.ENERGY_MIN * 1e-3))
                ax.plot(sync_ang_deviations, flux_Emax, 'b', label="E max={} keV".format(self.ENERGY_MAX * 1e-3))

            ax.set_title(toptitle)
            ax.set_xlabel(xtitle)
            ax.set_ylabel(ytitle)
            ax.set_xlim(sync_ang_deviations.min(), sync_ang_deviations.max())
            ax.legend(bbox_to_anchor=(1.1, 1.05))

            self.figure_canvas.draw()

            print("BendingMagnet: Photon bunch generated.\n")
            self.send("photon bunch", photon_bunch)

    def defaults(self):
        self.resetSettings()
        self.generate()
        return

    def get_doc(self):
        print("BendingMagnet: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'BendingMagnet'+'.txt')
        print("BendingMagnet: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("BendingMagnet: sys.platform did not yield an acceptable value!\n")
        os.system(command)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = OWBendingMagnet()
    w.show()
    app.exec()
    w.saveSettings()
