from PyQt4 import QtGui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import orangecanvas.resources as resources
import os
import sys
import numpy as np
from orangewidget.settings import Setting
from crystalpy.util.PhotonBunch import PhotonBunch
from orangewidget import gui, widget


class OWPhotonViewer(widget.OWWidget):
    name = "PhotonViewer"
    id = "orange.widgets.data.widget_name"
    description = ""
    icon = "icons/CrystalViewer.png"
    author = ""
    maintainer_email = "cappelli@esrf.fr"
    priority = 10
    category = ""
    keywords = ["PhotonViewer", "crystalpy", "viewer", "oasyscrystalpy"]
    inputs = [{"name": "photon bunch",
               "type": PhotonBunch,
               "doc": "",
               "handler": "_set_input"},
              ]

    SOURCE = Setting(0)  # Grid source.
    MODE = Setting(0)  # x-axis = deviations

    def __init__(self):
        super().__init__()

        self._input_available = False

        self.figure_canvas = None

        box0 = gui.widgetBox(self.controlArea, " ", orientation="horizontal")

        print("PhotonViewer: Photon viewer initialized.\n")
        # widget buttons: plot, help
        gui.button(box0, self, "Plot", callback=self.do_plot)
        gui.button(box0, self, "Help", callback=self.get_doc)

        box1 = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        gui.comboBox(box1, self, "SOURCE", addSpace=True,
                     items=["Grid-like source", "Monte Carlo source"],
                     orientation="horizontal")

        gui.comboBox(box1, self, "MODE", addSpace=True,
                     items=["Stokes(deviation)", "Stokes(energy)"],
                     orientation="horizontal")

    def _set_input(self, photon_bunch):
        if photon_bunch is not None:
            self._input_available = True
            print("PhotonViewer: The viewer has received the data.\n")
            # Retrieve the results from input data.
            self.photon_bunch = photon_bunch
            self.bunch_size = photon_bunch.get_array("number of photons")  # int
            self.energies = photon_bunch.get_array("energies")  # eV
            self.deviations = photon_bunch.get_array("deviations")  # urad
            self.deviations *= 1e+6
            self.s0 = photon_bunch.get_array("s0")
            self.s1 = photon_bunch.get_array("s1")
            self.s2 = photon_bunch.get_array("s2")
            self.s3 = photon_bunch.get_array("s3")

    def do_plot(self):

        if not self._input_available:
            raise Exception("PhotonViewer: Input data not available!\n")

        if self.figure_canvas is not None:
            self.mainArea.layout().removeWidget(self.figure_canvas)

        # Create subplots.
        fig, ((ax00, ax01), (ax10, ax11)) = plt.subplots(2, 2, sharex="all", sharey="all")
        self.figure_canvas = FigureCanvas(fig)
        self.mainArea.layout().addWidget(self.figure_canvas)

        # Deal with the special cases, where the plotting is straightforward.
        if self.photon_bunch.is_monochromatic(places=6):  # monochromatic bunch.
            print("PhotonViewer: Monochromatic bunch.\n")

            self.stokes_plot_deviations(deviations=self.deviations,
                                        s0=self.s0, s1=self.s1, s2=self.s2, s3=self.s3,
                                        ax00=ax00, ax01=ax01, ax10=ax10, ax11=ax11, figure_canvas=self.figure_canvas)

        elif self.photon_bunch.is_unidirectional():  # unidirectional bunch.
            print("PhotonViewer: Unidirectional bunch.\n")

            self.stokes_plot_energies(energies=self.energies,
                                      s0=self.s0, s1=self.s1, s2=self.s2, s3=self.s3,
                                      ax00=ax00, ax01=ax01, ax10=ax10, ax11=ax11, figure_canvas=self.figure_canvas)
        # General case:
        else:
            # Create the empty arrays.
            energies = np.array([])
            deviations = np.array([])
            s0 = np.array([])
            s1 = np.array([])
            s2 = np.array([])
            s3 = np.array([])

            if self.MODE == 0:  # stokes = f(deviations)

                if self.SOURCE == 0:  # Grid-like source.

                    energy = self.photon_bunch[0].energy()

                    for polarized_photon in self.photon_bunch:

                        if polarized_photon.energy() == energy:  # Iterate over a monochromatic part of the bunch.
                            deviations = np.append(deviations, polarized_photon.deviation())
                            stokes_vector = polarized_photon.stokesVector()
                            s0 = np.append(s0, stokes_vector.s0)
                            s1 = np.append(s1, stokes_vector.s1)
                            s2 = np.append(s2, stokes_vector.s2)
                            s3 = np.append(s3, stokes_vector.s3)

                        else:
                            self.stokes_plot_deviations(deviations * 1e+6, s0, s1, s2, s3, ax00, ax01, ax10, ax11, self.figure_canvas)
                            energy = polarized_photon.energy()  # Update the energy.
                            deviations = np.array([])  # Clear the arrays.
                            s0 = np.array([])
                            s1 = np.array([])
                            s2 = np.array([])
                            s3 = np.array([])

                elif self.SOURCE == 1:  # Monte Carlo source.

                    for polarized_photon in self.photon_bunch:

                        deviations = np.append(deviations, polarized_photon.deviation())
                        stokes_vector = polarized_photon.stokesVector()
                        s0 = np.append(s0, stokes_vector.s0)
                        s1 = np.append(s1, stokes_vector.s1)
                        s2 = np.append(s2, stokes_vector.s2)
                        s3 = np.append(s3, stokes_vector.s3)

                    self.scatter_plot_deviations(deviations * 1e+6, s0, s1, s2, s3, ax00, ax01, ax10, ax11, self.figure_canvas)

                else:
                    raise Exception("PhotonViewer: Source parameter outside of expected range!\n")

            elif self.MODE == 1:  # stokes = f(energies)

                if self.SOURCE == 0:  # Grid-like source.
                    # TODO: what to do in this case?
                    # for polarized_photon in self.photon_bunch:

                    #     energies = np.append(energies, polarized_photon.energy())
                    #     stokes_vector = polarized_photon.stokesVector()
                    #     s0 = np.append(s0, stokes_vector.s0)
                    #     s1 = np.append(s1, stokes_vector.s1)
                    #     s2 = np.append(s2, stokes_vector.s2)
                    #     s3 = np.append(s3, stokes_vector.s3)

                    # self.stokes_plot_energies(energies, s0, s1, s2, s3, ax00, ax01, ax10, ax11, self.figure_canvas)

                    raise Exception("PhotonViewer: This function has yet to be implemented!\n")

                elif self.SOURCE == 1:  # Monte Carlo source.

                    for polarized_photon in self.photon_bunch:
                        energies = np.append(energies, polarized_photon.energy())
                        stokes_vector = polarized_photon.stokesVector()
                        s0 = np.append(s0, stokes_vector.s0)
                        s1 = np.append(s1, stokes_vector.s1)
                        s2 = np.append(s2, stokes_vector.s2)
                        s3 = np.append(s3, stokes_vector.s3)

                    self.scatter_plot_energies(energies, s0, s1, s2, s3, ax00, ax01, ax10, ax11, self.figure_canvas)

                else:
                    raise Exception("PhotonViewer: Source parameter outside of expected range!\n")

            else:
                raise Exception("PhotonViewer: The plotting mode could not be interpreted!\n")

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

    @staticmethod
    def stokes_plot_deviations(deviations, s0, s1, s2, s3, ax00, ax01, ax10, ax11, figure_canvas):
        """
        Plot the Stokes vectors as a function of deviation.
        """
        # Plot.
        ax00.plot(deviations, s0, "-")
        ax01.plot(deviations, s1, "-")
        ax10.plot(deviations, s2, "-")
        ax11.plot(deviations, s3, "-")

        # Embellish.
        ax00.set_title("Stokes parameter S0")
        ax00.set_xlabel("deviation [urad]")
        # ax00.set_ylabel(plot_1d[0].title_y_axis)
        ax00.set_xlim([deviations.min(), deviations.max()])
        # ax00.set_ylim([-1.0, 1.0])

        ax01.set_title("Stokes parameter S1")
        ax01.set_xlabel("deviation [urad]")
        # ax01.set_ylabel(plot_1d[1].title_y_axis)
        ax01.set_xlim([deviations.min(), deviations.max()])
        # ax01.set_ylim([-1.0, 1.0])

        ax10.set_title("Stokes parameter S2")
        ax10.set_xlabel("deviation [urad]")
        # ax10.set_ylabel(plot_1d[2].title_y_axis)
        ax10.set_xlim([deviations.min(), deviations.max()])
        # ax10.set_ylim([-1.0, 1.0])

        ax11.set_title("Stokes parameter S3")
        ax11.set_xlabel("deviation [urad]")
        # ax11.set_ylabel(plot_1d[3].title_y_axis)
        ax11.set_xlim([deviations.min(), deviations.max()])
        # ax11.set_ylim([-1.0, 1.0])

        figure_canvas.draw()

    @staticmethod
    def scatter_plot_deviations(deviations, s0, s1, s2, s3, ax00, ax01, ax10, ax11, figure_canvas):
        """
        Plot the Stokes vectors as a function of deviation as scatter plots.
        """
        # Scatter plot.
        ax00.scatter(deviations, s0, marker="o")
        ax01.scatter(deviations, s1, marker="o")
        ax10.scatter(deviations, s2, marker="o")
        ax11.scatter(deviations, s3, marker="o")

        # Embellish.
        ax00.set_title("Stokes parameter S0")
        ax00.set_xlabel("deviation [urad]")
        # ax00.set_ylabel(plot_1d[0].title_y_axis)
        ax00.set_xlim([deviations.min(), deviations.max()])
        # ax00.set_ylim([-1.0, 1.0])

        ax01.set_title("Stokes parameter S1")
        ax01.set_xlabel("deviation [urad]")
        # ax01.set_ylabel(plot_1d[1].title_y_axis)
        ax01.set_xlim([deviations.min(), deviations.max()])
        # ax01.set_ylim([-1.0, 1.0])

        ax10.set_title("Stokes parameter S2")
        ax10.set_xlabel("deviation [urad]")
        # ax10.set_ylabel(plot_1d[2].title_y_axis)
        ax10.set_xlim([deviations.min(), deviations.max()])
        # ax10.set_ylim([-1.0, 1.0])

        ax11.set_title("Stokes parameter S3")
        ax11.set_xlabel("deviation [urad]")
        # ax11.set_ylabel(plot_1d[3].title_y_axis)
        ax11.set_xlim([deviations.min(), deviations.max()])
        # ax11.set_ylim([-1.0, 1.0])

        figure_canvas.draw()

    @staticmethod
    def stokes_plot_energies(energies, s0, s1, s2, s3, ax00, ax01, ax10, ax11, figure_canvas):
        """
        Plot the Stokes vectors as a function of energy.
        """
        # Plot.
        ax00.plot(energies, s0, "-")
        ax01.plot(energies, s1, "-")
        ax10.plot(energies, s2, "-")
        ax11.plot(energies, s3, "-")

        # Embellish.
        ax00.set_title("Stokes parameter S0")
        ax00.set_xlabel("energy [eV]")
        # ax00.set_ylabel(plot_1d[0].title_y_axis)
        ax00.set_xlim([energies.min(), energies.max()])
        # ax00.set_ylim([-1.0, 1.0])

        ax01.set_title("Stokes parameter S1")
        ax01.set_xlabel("energy [eV]")
        # ax01.set_ylabel(plot_1d[1].title_y_axis)
        ax01.set_xlim([energies.min(), energies.max()])
        # ax01.set_ylim([-1.0, 1.0])

        ax10.set_title("Stokes parameter S2")
        ax10.set_xlabel("energy [eV]")
        # ax10.set_ylabel(plot_1d[2].title_y_axis)
        ax10.set_xlim([energies.min(), energies.max()])
        # ax10.set_ylim([-1.0, 1.0])

        ax11.set_title("Stokes parameter S3")
        ax11.set_xlabel("energy [eV]")
        # ax11.set_ylabel(plot_1d[3].title_y_axis)
        ax11.set_xlim([energies.min(), energies.max()])
        # ax11.set_ylim([-1.0, 1.0])

        figure_canvas.draw()

    @staticmethod
    def scatter_plot_energies(energies, s0, s1, s2, s3, ax00, ax01, ax10, ax11, figure_canvas):
        """
        Plot the Stokes vectors as a function of energy as scatter plots.
        """
        # Scatter plot.
        ax00.scatter(energies, s0, marker="o")
        ax01.scatter(energies, s1, marker="o")
        ax10.scatter(energies, s2, marker="o")
        ax11.scatter(energies, s3, marker="o")

        # Embellish.
        ax00.set_title("Stokes parameter S0")
        ax00.set_xlabel("energy [eV]")
        # ax00.set_ylabel(plot_1d[0].title_y_axis)
        ax00.set_xlim([energies.min(), energies.max()])
        # ax00.set_ylim([-1.0, 1.0])

        ax01.set_title("Stokes parameter S1")
        ax01.set_xlabel("energy [eV]")
        # ax01.set_ylabel(plot_1d[1].title_y_axis)
        ax01.set_xlim([energies.min(), energies.max()])
        # ax01.set_ylim([-1.0, 1.0])

        ax10.set_title("Stokes parameter S2")
        ax10.set_xlabel("energy [eV]")
        # ax10.set_ylabel(plot_1d[2].title_y_axis)
        ax10.set_xlim([energies.min(), energies.max()])
        # ax10.set_ylim([-1.0, 1.0])

        ax11.set_title("Stokes parameter S3")
        ax11.set_xlabel("energy [eV]")
        # ax11.set_ylabel(plot_1d[3].title_y_axis)
        ax11.set_xlim([energies.min(), energies.max()])
        # ax11.set_ylim([-1.0, 1.0])

        figure_canvas.draw()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    ow = OWPhotonViewer()

    # TODO: write an example for the new widget.
    # a = np.array([
    #     [8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04],
    #     [1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
    #     ])
    # ow.do_plot(a)
    # ow.show()
    # app.exec_()
    # ow.saveSettings()