import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import orangecanvas.resources as resources
import os
import sys
import numpy as np
from orangewidget.settings import Setting
from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from orangewidget import gui, widget


class PlotType:
    """Contains the different plot types that can be plotted by the viewer."""
    # STOKES_DEVIATION = {'subplots': (2, 2), 'x values': "deviations", 'y values': "stokes",              'style': "grid"}
    STOKES_DEVIATION = {'subplots': (2, 2), 'x values': "deviations", 'y values': "stokes",              'style': "scatter"}
    STOKES_ENERGY = {   'subplots': (2, 2), 'x values': "energies",   'y values': "stokes",              'style': "scatter"}
    # POLAR_DEVIATION = { 'subplots': (1, 1), 'x values': "deviations", 'y values': "polarization degrees", 'style': "grid"}
    POLAR_DEVIATION = { 'subplots': (1, 1), 'x values': "deviations", 'y values': "polarization degrees", 'style': "scatter"}
    POLAR_ENERGY = {    'subplots': (1, 1), 'x values': "energies",   'y values': "polarization degrees", 'style': "scatter"}


class OWPhotonViewer(widget.OWWidget):
    name = "PhotonViewer"
    id = "orange.widgets.data.widget_name"
    description = ""
    icon = "icons/PhotonViewer.png"
    author = ""
    maintainer_email = "cappelli@esrf.fr"
    priority = 40
    category = ""
    keywords = ["PhotonViewer", "crystalpy", "viewer", "oasyscrystalpy"]
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "doc": "",
               "handler": "_set_input"},
              ]

    PLOT_TYPE = Setting(0)  # Stokes parameters (deviation)

    def __init__(self):
        super().__init__()

        self._input_available = False

        self.figure_canvas = None

        print("PhotonViewer: Photon viewer initialized.\n")

        # box0 = gui.widgetBox(self.controlArea, " ", orientation="horizontal")
        # # box0 = gui.widgetBox(self.controlArea, " ", orientation="vertical")
        #

        # # widget buttons: plot, help
        # gui.button(box0, self, "Plot", callback=self.do_plot)
        # gui.button(box0, self, "Help", callback=self.get_doc)

        box1 = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        gui.comboBox(box1, self, "PLOT_TYPE", addSpace=True,
                     items=["Stokes(deviation)", "Stokes(energy)",
                            "Polarization degree(deviation)", "Polarization degree(energy)"],
                     orientation="horizontal",callback=self.do_plot)

    def _set_input(self, photon_bunch):
        """This function is called when the widget receives an input."""
        if photon_bunch is not None:
            self._input_available = True  # The input is now available.
            print("PhotonViewer: The viewer has received the data.\n")

            # Retrieve the results from input data.
            self.photon_bunch = photon_bunch
            self.bunch_size = photon_bunch.getArrayByKey("number of photons")  # int
            self.energies = photon_bunch.getArrayByKey("energies")  # eV
            self.deviations = photon_bunch.getArrayByKey("deviations")  # urad
            self.deviations *= 1e+6
            self.stokes_vectors = [photon_bunch.getArrayByKey("s0"),
                                   photon_bunch.getArrayByKey("s1"),
                                   photon_bunch.getArrayByKey("s2"),
                                   photon_bunch.getArrayByKey("s3")]
            self.polarization_degrees = photon_bunch.getArrayByKey("polarization degree")

            self.do_plot()

    def get_plot_type(self):

        if self.PLOT_TYPE == 0:
            return PlotType.STOKES_DEVIATION

        elif self.PLOT_TYPE == 1:
            return PlotType.STOKES_ENERGY

        elif self.PLOT_TYPE == 2:
            return PlotType.POLAR_DEVIATION

        elif self.PLOT_TYPE == 3:
            return PlotType.POLAR_ENERGY

        else:
            raise ValueError("PhotonViewer: Plot Type not recognized!\n")

    def do_plot(self):
        try:
            # Check whether the input is available.
            if not self._input_available:
                raise Exception("PhotonViewer: Input data not available!\n")

            # If there is already a FigureCanvas, remove it so it can be substituted by a new one.
            if self.figure_canvas is not None:
                self.mainArea.layout().removeWidget(self.figure_canvas)

            plot_type = self.get_plot_type()

            # Create the subplots according to the PlotType.
            n = plot_type['subplots'][0]
            m = plot_type['subplots'][1]
            fig, axes = plt.subplots(n, m, sharex="all", sharey="all")
            self.axes = np.array(axes).flatten()

            self.figure_canvas = FigureCanvas(fig)
            self.mainArea.layout().addWidget(self.figure_canvas)

            #
            # Initialize plotting parameters according to PlotType.
            #
            if plot_type['x values'] == "deviations":
                x_values = self.deviations
                x_label = "deviations [urad]"

            elif plot_type['x values'] == "energies":
                x_values = self.energies
                x_label = "energies [eV]"

            else:
                raise Exception("PhotonViewer: The PlotType class might be badly defined!\n")

            if plot_type['y values'] == "stokes":
                y_values_array = self.stokes_vectors
                titles = ["Stokes parameter S0",
                          "Stokes parameter S1",
                          "Stokes parameter S2",
                          "Stokes parameter S3"]

            elif plot_type['y values'] == "polarization degrees":
                y_values_array = [self.polarization_degrees]
                titles = ["Degree of circular polarization"]

            else:
                raise Exception("PhotonViewer: The PlotType class might be badly defined!\n")

            #
            # Deal with the special cases, where the plotting is straightforward.
            #
            if self.photon_bunch.isMonochromatic(places=6) or \
                    self.photon_bunch.isUnidirectional():  # unidirectional or monochromatic.

                self.plot(x_values, y_values_array, x_label=x_label, titles=titles)

            #
            # General case.
            #
            else:
                if plot_type['x values'] == "energies":

                    self.plot(x_values, y_values_array, x_label=x_label, titles=titles)

                elif plot_type['x values'] == "deviations":

                    # Create the empty arrays.
                    x_values = np.array([])
                    polarization_degrees = np.array([])
                    s0 = np.array([])
                    s1 = np.array([])
                    s2 = np.array([])
                    s3 = np.array([])

                    energy = self.photon_bunch[0].energy()

                    for i in range(self.photon_bunch.getNumberOfPhotons()):
                        polarized_photon = self.photon_bunch.getPhotonIndex(i)
                        if polarized_photon.energy() == energy:  # Iterate over a monochromatic portion.
                            x_values = np.append(x_values, np.multiply(polarized_photon.deviation(), 1e+6))
                            polarization_degrees = np.append(polarization_degrees,
                                                             polarized_photon.polarizationDegree())
                            stokes_vector = polarized_photon.stokesVector()
                            s0 = np.append(s0, stokes_vector.s0)
                            s1 = np.append(s1, stokes_vector.s1)
                            s2 = np.append(s2, stokes_vector.s2)
                            s3 = np.append(s3, stokes_vector.s3)
                        else:
                            if plot_type['y values'] == "stokes":
                                y_values_array = [s0, s1, s2, s3]

                            elif plot_type['y values'] == "polarization degrees":
                                y_values_array = [polarization_degrees]

                            self.plot(x_values, y_values_array, x_label=x_label, titles=titles)

                            energy = polarized_photon.energy()  # Update the energy.
                            x_values = np.array([])  # Clear the arrays.
                            polarization_degrees = np.array([])
                            s0 = np.array([])
                            s1 = np.array([])
                            s2 = np.array([])
                            s3 = np.array([])

        except Exception as e:
            QtGui.QMessageBox.critical(self, "Error", str(e))

    def plot(self, x_values, y_values_array, x_label="", y_label="", titles=None):
        """y_values_array can be an array of arrays."""

        for index in range(0, len(self.axes)):

            if self.get_plot_type()['style'] == "grid":
                self.axes[index].plot(x_values, y_values_array[index], "-")

            elif self.get_plot_type()['style'] == "scatter":
                self.axes[index].scatter(x_values, y_values_array[index], marker="o")

            # Embellish.
            self.axes[index].set_xlabel(x_label)
            self.axes[index].set_ylabel(y_label)
            self.axes[index].set_title(titles[index])
            self.axes[index].set_xlim([x_values.min(), x_values.max()])

        self.figure_canvas.draw()

    def get_doc(self):
        print("PhotonViewer: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'CrystalViewer'+'.txt')
        print("PhotonViewer: Opening file %s\n" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("PhotonViewer: sys.platform did not yield an acceptable value!\n")
        os.system(command)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    from crystalpy.util.Vector import Vector
    from crystalpy.util.StokesVector import StokesVector
    from crystalpy.util.PolarizedPhoton import PolarizedPhoton
    from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch

    app = QApplication([])
    ow = OWPhotonViewer()

    nphotons = 10

    from crystalpy.util.Vector import Vector
    from crystalpy.util.StokesVector import StokesVector

    bunch = PolarizedPhotonBunch([])
    for i in range(nphotons):
        polarized_photon = PolarizedPhoton(energy_in_ev=1000.0+i,
                                           direction_vector=Vector(0,1.0,0),
                                           stokes_vector=StokesVector([1.0,0,1.0,0]))
        bunch.addPhoton(polarized_photon)


    ow._set_input(bunch)
    ow.do_plot()
    ow.show()

    app.exec_()
    ow.saveSettings()
