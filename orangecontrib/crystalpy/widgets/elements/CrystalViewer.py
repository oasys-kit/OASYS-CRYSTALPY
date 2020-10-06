# TODO: fare in modo di poter settare alcuni parametri del plot come i range per la fase,
# TODO: aggiungere la possibilita' di fare plot al variare della energia o anche plot 2d al variare di energia e angoli.

from orangewidget import widget, gui
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import orangecanvas.resources as resources
import os
import sys
from crystalpy.examples.PlotData1D import PlotData1D
from orangecontrib.crystalpy.util.MailingBox import MailingBox


class OWCrystalViewer(widget.OWWidget):
    name = "Crystal Calculator Viewer"
    id = "orange.widgets.data.widget_name"
    description = ""
    icon = "icons/CrystalViewer.png"
    author = ""
    maintainer_email = "cappelli@esrf.fr"
    priority = 55
    category = ""
    keywords = ["CrystalViewer", "crystalpy", "viewer"]
    inputs = [{"name": "diffraction data",
               "type": MailingBox,
               "doc": "",
               "handler": "_set_results"},
              ]

    def __init__(self):
        super().__init__()

        self._input_available = False

        print("CrystalViewer: Initializing the figure canvas...\n")
        self.figure_canvas = None

        print("CrystalViewer: Initializing the plot type...\n")
        self._init_plot_type()  # initialize to None the fields in the plot_type dict

        box0 = gui.widgetBox(self.controlArea, " ", orientation="vertical")

        # widget buttons: Intensity&Phase plot, Stokes parameters plot, degree of circular polarization plot, help
        gui.button(box0, self, "Intensity & phase", callback=self._set_intensity_phase_plot)
        gui.button(box0, self, "Stokes parameters", callback=self._set_stokes_plot)
        gui.button(box0, self, "Circular polarization", callback=self._set_polarization_degree_plot)
        # gui.button(box0, self, "Help", callback=self.get_doc)
        # self.process_showers()

    def _set_results(self, results):
        if results is not None:
            self._input_available = True
            print("CrystalViewer: The viewer has received the data.\n")
            # Retrieve the results from input data.
            self.diffraction_result = results.diffraction_result
            self.mueller_result = results.mueller_result
            self.do_plot()

    def _init_plot_type(self):
        self.plot_type = {
            "intensity phase": True,
            "stokes parameters": None,
            "circular polarization degree": None
        }

    def _clean_plot_type(self):
        self.plot_type = {
            "intensity phase": None,
            "stokes parameters": None,
            "circular polarization degree": None
        }

    def _set_intensity_phase_plot(self):
        self._clean_plot_type()  # clean the dictionary
        print("CrystalViewer: Plot type -> intensity & phase plot.\n")
        self.plot_type["intensity phase"] = True
        self.do_plot()

    def _set_stokes_plot(self):
        self._clean_plot_type()  # clean the dictionary
        print("CrystalViewer: Plot type -> Stokes parameters plot.\n")
        self.plot_type["stokes parameters"] = True
        self.do_plot()

    def _set_polarization_degree_plot(self):
        self._clean_plot_type()  # clean the dictionary
        print("CrystalViewer: Plot type -> degree of circular polarization plot.\n")
        self.plot_type["circular polarization degree"] = True
        self.do_plot()

    def do_plot(self):

        if not self._input_available:
            raise Exception("CrystalViewer: Input data not available!\n")

        # Create PlotData1D objects.
        diffraction_plots = self.plot_diffraction_1d(self.diffraction_result, deg=True)
        stokes_plots = self.plot_stokes_1d(self.mueller_result)

        # Plotting according to user's choice.
        if self.plot_type["intensity phase"]:
            fig = self.intensity_phase_plot(diffraction_plots)

        elif self.plot_type["stokes parameters"]:
            fig = self.stokes_plot(stokes_plots)

        elif self.plot_type["circular polarization degree"]:
            fig = self.polarization_degree_plot(stokes_plots)

        else:
            raise Exception("CrystalViewer: The plot type is not well defined!")

        if self.figure_canvas is not None:
            self.mainArea.layout().removeWidget(self.figure_canvas)
        self.figure_canvas = FigureCanvas(fig)  # plt.figure()
        self.mainArea.layout().addWidget(self.figure_canvas)
        self.figure_canvas.draw()

    def get_doc(self):
        print("CrystalViewer: help pressed.\n")
        home_doc = resources.package_dirname("orangecontrib.oasyscrystalpy") + "/doc_files/"
        filename1 = os.path.join(home_doc, 'CrystalViewer'+'.txt')
        print("CrystalViewer: Opening file %s" % filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        else:
            raise Exception("CrystalViewer: sys.platform did not yield an acceptable value!")
        os.system(command)

    def intensity_phase_plot(self, plot_1d):
        """
        Plot the diffraction results.
        :param plot_1d: PlotData1D object.
        """
        # Create subplots.
        fig, ((ax1_intensity, ax2_intensity, ax3_intensity),
              (ax1_phase, ax2_phase, ax3_phase)) = plt.subplots(2, 3)

        # Subplot 1-1: s-polarization intensity.
        ax1_intensity.plot(plot_1d[0].x, plot_1d[0].y, "b-")
        ax1_intensity.set_title(plot_1d[0].title)
        ax1_intensity.set_xlabel(plot_1d[0].title_x_axis)
        ax1_intensity.set_ylabel(plot_1d[0].title_y_axis)
        ax1_intensity.set_xlim([plot_1d[0].x_min, plot_1d[0].x_max])
        ax1_intensity.set_ylim([0, 1])

        # Subplot 2-1: s-polarization phase.
        ax1_phase.plot(plot_1d[3].x, plot_1d[3].y, "g-")
        ax1_phase.set_title(plot_1d[3].title)
        ax1_phase.set_xlabel(plot_1d[3].title_x_axis)
        ax1_phase.set_ylabel(plot_1d[3].title_y_axis)
        ax1_phase.set_xlim([plot_1d[3].x_min, plot_1d[3].x_max])
        ax1_phase.set_ylim([-180, 180])

        # Subplot 1-2: p-polarization intensity.
        ax2_intensity.plot(plot_1d[1].x, plot_1d[1].y, "b-")
        ax2_intensity.set_title(plot_1d[1].title)
        ax2_intensity.set_xlabel(plot_1d[1].title_x_axis)
        ax2_intensity.set_ylabel(plot_1d[1].title_y_axis)
        ax2_intensity.set_xlim([plot_1d[1].x_min, plot_1d[1].x_max])
        ax2_intensity.set_ylim([0, 1])

        # Subplot 2-2: p-polarization phase.
        ax2_phase.plot(plot_1d[4].x, plot_1d[4].y, "g-")
        ax2_phase.set_title(plot_1d[4].title)
        ax2_phase.set_xlabel(plot_1d[4].title_x_axis)
        ax2_phase.set_ylabel(plot_1d[4].title_y_axis)
        ax2_phase.set_xlim([plot_1d[4].x_min, plot_1d[4].x_max])
        ax2_phase.set_ylim([-180, 180])

        # Subplot 1-3: s-p intensity ratio.
        ax3_intensity.plot(plot_1d[2].x, plot_1d[2].y, "b-")
        ax3_intensity.set_title(plot_1d[2].title)
        ax3_intensity.set_xlabel(plot_1d[2].title_x_axis)
        ax3_intensity.set_ylabel(plot_1d[2].title_y_axis)
        ax3_intensity.set_xlim([plot_1d[2].x_min, plot_1d[2].x_max])
        ax3_intensity.set_ylim([0, 1])

        # Subplot 2-3: s-p phase difference.
        ax3_phase.plot(plot_1d[5].x, plot_1d[5].y, "g-")
        ax3_phase.set_title(plot_1d[5].title)
        ax3_phase.set_xlabel(plot_1d[5].title_x_axis)
        ax3_phase.set_ylabel(plot_1d[5].title_y_axis)
        ax3_phase.set_xlim([plot_1d[5].x_min, plot_1d[5].x_max])
        ax3_phase.set_ylim([-180, 180])

        return fig

    def stokes_plot(self, plot_1d):
        """
        Plot the Stokes vectors.
        :param plot_1d: PlotData1D object.
        """
        # Create subplots.
        fig, ((ax00, ax01), (ax10, ax11)) = plt.subplots(2, 2, sharex="all", sharey="all")

        ax00.plot(plot_1d[0].x, plot_1d[0].y, "-")
        ax00.set_title(plot_1d[0].title)
        ax00.set_xlabel(plot_1d[0].title_x_axis)
        ax00.set_ylabel(plot_1d[0].title_y_axis)
        ax00.set_xlim([plot_1d[0].x_min, plot_1d[0].x_max])
        # ax00.set_ylim([-1.0, 1.0])

        ax01.plot(plot_1d[1].x, plot_1d[1].y, "-")
        ax01.set_title(plot_1d[1].title)
        ax01.set_xlabel(plot_1d[1].title_x_axis)
        ax01.set_ylabel(plot_1d[1].title_y_axis)
        ax01.set_xlim([plot_1d[1].x_min, plot_1d[1].x_max])
        # ax01.set_ylim([-1.0, 1.0])

        ax10.plot(plot_1d[2].x, plot_1d[2].y, "-")
        ax10.set_title(plot_1d[2].title)
        ax10.set_xlabel(plot_1d[2].title_x_axis)
        ax10.set_ylabel(plot_1d[2].title_y_axis)
        ax10.set_xlim([plot_1d[2].x_min, plot_1d[2].x_max])
        # ax10.set_ylim([-1.0, 1.0])

        ax11.plot(plot_1d[3].x, plot_1d[3].y, "-")
        ax11.set_title(plot_1d[3].title)
        ax11.set_xlabel(plot_1d[3].title_x_axis)
        ax11.set_ylabel(plot_1d[3].title_y_axis)
        ax11.set_xlim([plot_1d[3].x_min, plot_1d[3].x_max])
        # ax11.set_ylim([-1.0, 1.0])

        return fig

    def polarization_degree_plot(self, plot_1d):
        """
        Plot the degree of circular polarization.
        :param plot_1d: PlotData1D object.
        """
        fig, polarization_degree = plt.subplots(1, 1)
        polarization_degree.plot(plot_1d[4].x, plot_1d[4].y, "b-")
        polarization_degree.set_title(plot_1d[4].title)
        polarization_degree.set_xlabel(plot_1d[4].title_x_axis)
        polarization_degree.set_ylabel(plot_1d[4].title_y_axis)
        polarization_degree.set_xlim([plot_1d[4].x_min, plot_1d[4].x_max])
        polarization_degree.set_ylim([-1, 1])

        return fig

    def plot_diffraction_1d(self, result, deg):
        """
        Returns this result instance in PlotData1D representation.
        :param deg: if False the phase is expressed in radians, if True in degrees.
        """
        # Distinguish between the strings "phase in deg" and "phase in rad".
        if deg:
            phase_string = "Phase in deg"
        else:
            phase_string = "Phase in rad"

        # Retrieve setup information.
        info_dict = result.diffractionSetup().toDictionary()
        info_dict["Bragg angle"] = str(result.braggAngle())

        # Retrieve angles of the results.
        angles_in_um = [i * 1e+6 for i in result.angleDeviations()]

        # Retrieve minimum and maximum.
        x_min = result.angleDeviations().min() * 1e+6
        x_max = result.angleDeviations().max() * 1e+6

        # Define inner function to duplicate info for every plot.
        def addPlotInfo(info_dict, energy, angles_in_um, data):
            plot_data = PlotData1D(data[0], data[1], data[2])
            plot_data.set_x(angles_in_um)
            plot_data.set_y(data[3])
            plot_data.set_x_min(x_min)
            plot_data.set_x_max(x_max)
            for key, value in info_dict.items():
                plot_data.add_plot_info(key, value)
            plot_data.add_plot_info("Energy", str(energy))
            return plot_data

        plots = []
        for energy in result.energies():
            # Intensity S polarization.
            categories = []

            s_intensity = ("Intensity - Polarization S",
                           "Angle deviation in urad",
                           "Intensity",
                           result.sIntensityByEnergy(energy))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, s_intensity))

            p_intensity = ("Intensity - Polarization P",
                           "Angle deviation in urad",
                           "Intensity",
                           result.pIntensityByEnergy(energy))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, p_intensity))

            intensity_difference = ("Intensity ratio",
                                    "Angle deviation in urad",
                                    "Intensity",
                                    result.differenceIntensityByEnergy(energy))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, intensity_difference))

            s_phase = ("Phase - Polarization S",
                       "Angle deviation in urad",
                       phase_string,
                       result.sPhaseByEnergy(energy, deg))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, s_phase))

            p_phase = ("Phase - Polarization P",
                       "Angle deviation in urad",
                       phase_string,
                       result.pPhaseByEnergy(energy, deg))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, p_phase))

            phase_difference = ("Phase difference",
                                "Angle deviation in urad",
                                phase_string,
                                result.differencePhaseByEnergy(energy, deg))
            plots.append(addPlotInfo(info_dict, energy, angles_in_um, phase_difference))

        return plots

    def plot_stokes_1d(self, result):
        """
        Returns this result instance in PlotData1D representation.
        """
        # Retrieve setup information.
        info_dict = result.diffraction_setup.toDictionary()
        info_dict["Bragg angle"] = str(result.diffraction_result.braggAngle())

        # Retrieve angles of the results.
        angles_in_urad = [i * 1e+6 for i in result.angle_deviations()]

        # Retrieve minimum and maximum.
        x_min = result.angle_deviations().min() * 1e+6
        x_max = result.angle_deviations().max() * 1e+6

        # Define inner function to duplicate info for every plot.
        def add_all_plot_info(info_dict, energy, angles_in_urad, data):
            plot_data = PlotData1D(data[0], data[1], data[2])
            plot_data.set_x(angles_in_urad)
            plot_data.set_y(data[3])
            plot_data.set_x_min(x_min)
            plot_data.set_x_max(x_max)
            for key, value in info_dict.items():  # dict.items() returns a list of (key, value) tuples
                plot_data.add_plot_info(key, value)
            plot_data.add_plot_info("Energy", str(energy))
            return plot_data

        plots = list()
        for energy in result.energies():
            s0 = ("Stokes parameter S0",
                  "Angle deviation in urad",
                  "S0",
                  result.s0_by_energy(energy))
            plots.append(add_all_plot_info(info_dict, energy, angles_in_urad, s0))

            s1 = ("Stokes parameter S1",
                  "Angle deviation in urad",
                  "S1",
                  result.s1_by_energy(energy))
            plots.append(add_all_plot_info(info_dict, energy, angles_in_urad, s1))

            s2 = ("Stokes parameter S2",
                  "Angle deviation in urad",
                  "S2",
                  result.s2_by_energy(energy))
            plots.append(add_all_plot_info(info_dict, energy, angles_in_urad, s2))

            s3 = ("Stokes parameter S3",
                  "Angle deviation in urad",
                  "S3",
                  result.s3_by_energy(energy))
            plots.append(add_all_plot_info(info_dict, energy, angles_in_urad, s3))

            polarization_degree = ("Degree of circular polarization",
                                   "Angle deviation in urad",
                                   "Circular polarization",
                                   result.polarization_degree_by_energy(energy))
            plots.append(add_all_plot_info(info_dict, energy, angles_in_urad, polarization_degree))

        return plots


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    ow = OWCrystalViewer()
    ow.show()
    app.exec()
    ow.saveSettings()

    # TODO: write an example for the new widget.
    # a = np.array([
    #     [8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04],
    #     [1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
    #     ])
    # ow.do_plot(a)
    # ow.show()
    # app.exec_()
    # ow.saveSettings()
