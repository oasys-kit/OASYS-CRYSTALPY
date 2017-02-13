__author__ = 'srio'
import sys

from oasys.widgets import widget

from orangewidget import  gui
from PyQt4 import QtGui

from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch, PolarizedPhoton
from crystalpy.util.Vector import Vector
from crystalpy.util.StokesVector import StokesVector

from orangecontrib.shadow.util.shadow_objects import ShadowBeam, EmittingStream, TTYGrabber
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot


class ShadowConverter(widget.OWWidget):

    name = "ShadowConverter"
    description = "Converts PolarizedPhotonBunch to Shadow Beam and back"
    icon = "icons/converter.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 10
    category = "crystalpy"
    keywords = ["PhotonViewer", "crystalpy", "viewer", "oasyscrystalpy", "shadowOui"]

    # the widget takes in a collection of Photon objects and
    # sends out an object of the same type made up of scattered photons.
    inputs = [{"name": "photon bunch",
               "type": PolarizedPhotonBunch,
               "handler": "_set_input_photon_bunch",
               "doc": ""},
              {"name": "Input Beam",
               "type": ShadowBeam,
               "handler": "_set_input_shadow_beam",
               "doc": ""},
              ]

    outputs = [{"name": "photon bunch",
                "type": PolarizedPhotonBunch,
                "doc": "transfer diffraction results"},
                {"name":"Beam",
                "type":ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"},
               ]

    want_main_area = 0
    want_control_area = 1

    def __init__(self):

         self.setFixedWidth(600)
         self.setFixedHeight(100)

         gui.separator(self.controlArea, height=20)
         gui.label(self.controlArea, self, "         CONVERSION POINT: PolarizedPhotonBunch <-> ShadowOuiBeam", orientation="horizontal")
         gui.rubber(self.controlArea)

    def _set_input_photon_bunch(self, photon_bunch):
        if photon_bunch is not None:
            print("<><> CONVERTER has received PolarizedPhotonBunch)")
            self._input_available = True
            self.incoming_bunch = photon_bunch
            self.send_photon_bunch(photon_bunch)



    def _set_input_shadow_beam(self, beam):
        if ShadowCongruence.checkEmptyBeam(beam):
            if ShadowCongruence.checkGoodBeam(beam):
                print("<><> CONVERTER has received GOOD Shadow BEAM)")
                self._input_available = True
                self.incoming_shadow_beam = beam
                self.send_shadow_beam(beam)
                #
                # translate
                #
                photon_bunch = self.from_shadow_beam_to_photon_bunch()
                self.send_photon_bunch(photon_bunch)
            else:
                QtGui.QMessageBox.critical(self, "Error",
                                           "Data not displayable: No good rays or bad content",
                                           QtGui.QMessageBox.Ok)


    def send_photon_bunch(self, photon_bunch):
        print("<><> sending photon bunch")
        self.send("photon bunch", photon_bunch)

    def send_shadow_beam(self, shadow_beam):
        print("<><> sending shadow beam")
        self.send("Beam", shadow_beam)

    def from_shadow_beam_to_photon_bunch(self):

        vx = self.incoming_shadow_beam._beam.getshcol(4,nolost=1)
        vy = self.incoming_shadow_beam._beam.getshcol(5,nolost=1)
        vz = self.incoming_shadow_beam._beam.getshcol(6,nolost=1)

        s0 = self.incoming_shadow_beam._beam.getshcol(30,nolost=1)
        s1 = self.incoming_shadow_beam._beam.getshcol(31,nolost=1)
        s2 = self.incoming_shadow_beam._beam.getshcol(32,nolost=1)
        s3 = self.incoming_shadow_beam._beam.getshcol(33,nolost=1)
        energies = self.incoming_shadow_beam._beam.getshcol(11,nolost=1)

        photon_bunch = PolarizedPhotonBunch([])
        photons_list = list()
        for i,energy in enumerate(energies):
            photon = PolarizedPhoton(energy_in_ev=energies[i],
                                     direction_vector=Vector(vx[i],vy[i],vz[i]),
                                     stokes_vector=StokesVector([s0[i],s1[i],s2[i],s3[i]]))
            #photon_bunch.add(photon)
            print("<><> appending photon",i)
            photons_list.append(photon)


        photon_bunch.add(photons_list)

        return photon_bunch





if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    ow = ShadowConverter()
    ow.show()
    a.exec_()
    ow.saveSettings()
