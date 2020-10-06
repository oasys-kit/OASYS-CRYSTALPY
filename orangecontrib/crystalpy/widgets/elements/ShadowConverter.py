__author__ = 'srio'
import sys
import numpy
import scipy.constants as codata

from oasys.widgets import widget

from orangewidget import  gui

from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.util.PolarizedPhoton import PolarizedPhoton
from crystalpy.util.Vector import Vector
from crystalpy.util.StokesVector import StokesVector

from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from oasys.util.oasys_util import EmittingStream, TTYGrabber
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot

import Shadow
from orangecontrib.shadow.util.shadow_objects import ShadowBeam, ShadowOpticalElement, ShadowOEHistoryItem


class ShadowConverter(widget.OWWidget):

    name = "ShadowConverter"
    description = "Converts PolarizedPhotonBunch to Shadow Beam and back"
    icon = "icons/converter.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 45
    category = "crystalpy"
    keywords = ["PhotonViewer", "crystalpy", "viewer", "shadowOui"]

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
            #
            # translate
            #
            shadow_beam = self.from_photon_bunch_to_shadow()
            self.send_shadow_beam(shadow_beam)


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
        self.send("photon bunch", photon_bunch)

    def send_shadow_beam(self, shadow_beam):
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
            photon = PolarizedPhoton(energy_in_ev=energy,
                                     direction_vector=Vector(vx[i],vy[i],vz[i]),
                                     stokes_vector=StokesVector([s0[i],s1[i],s2[i],s3[i]]))
            #photon_bunch.add(photon)
            # print("<><> appending photon",i)
            photons_list.append(photon)


        photon_bunch.addPhotonsFromList(photons_list)

        return photon_bunch

    def create_dummy_oe(self):
        empty_element = ShadowOpticalElement.create_empty_oe()

        # TODO: check this
        empty_element._oe.DUMMY = 100.0 # self.workspace_units_to_cm

        empty_element._oe.T_SOURCE     = 0.0
        empty_element._oe.T_IMAGE = 0.0
        empty_element._oe.T_INCIDENCE  = 0.0
        empty_element._oe.T_REFLECTION = 180.0
        empty_element._oe.ALPHA        = 0.0

        empty_element._oe.FWRITE = 3
        empty_element._oe.F_ANGLE = 0

        return empty_element

    def from_photon_bunch_to_shadow(self):

        photon_beam = self.incoming_bunch

        N =        photon_beam.getArrayByKey("number of photons")
        energies = photon_beam.getArrayByKey("energies")
        S0 =       photon_beam.getArrayByKey("s0")
        S1 =       photon_beam.getArrayByKey("s1")
        S2 =       photon_beam.getArrayByKey("s2")
        S3 =       photon_beam.getArrayByKey("s3")
        vx =       photon_beam.getArrayByKey("vx")
        vy =       photon_beam.getArrayByKey("vy")
        vz =       photon_beam.getArrayByKey("vz")

        beam = Shadow.Beam(N)
        A2EV = 2.0 *  numpy.pi / (codata.h*codata.c/codata.e*1e2)

        for i in range(N):
            s0 = S0[i]
            s1 = S1[i]
            s2 = S2[i]
            s3 = S3[i]
            energy = energies[i]


            if (numpy.abs(s1**2 + s2**2 + s3**2 - s0**2) > 1e-4 ):
                s0 = numpy.sqrt(s1**2 + s2**2 + s3**2)
                print("Warning: Beam is not fully polarized.")

            Ex2 = 0.5 * (s0 + s1)
            Ez2 = 0.5 * (s0 - s1)

            Ex = numpy.sqrt( Ex2 )
            Ez = numpy.sqrt( Ez2 )

            if s0 == s1:
                sin2delta = 0.0
            else:
                sin2delta = -0.5 * ( (s2**2 - s3**2) / ( 4 * Ex2 * Ez2) - 1)

            delta = numpy.arcsin( numpy.sign(s3) * numpy.sqrt(sin2delta) )
            beam.rays[i,0] = 0.0 # x
            beam.rays[i,1] = 0.0 # x
            beam.rays[i,2] = 0.0 # x
            beam.rays[i,3] = vx[i]  # v
            beam.rays[i,4] = vy[i]  # v
            beam.rays[i,5] = vz[i]  # v
            beam.rays[i,6] = Ex  # Es
            beam.rays[i,7] = 0.0 # Es
            beam.rays[i,8] = 0.0 # Es
            beam.rays[i,9] = 1.0 # lost ray flag
            beam.rays[i,10] = A2EV * energy # k
            beam.rays[i,11] = i  # ray index
            beam.rays[i,12] = 0.0 # path length
            beam.rays[i,13] = 0.0   # phase-s
            beam.rays[i,14] = delta # phase-ps
            beam.rays[i,15] = 0.0   # Ep
            beam.rays[i,16] = 0.0   # Ep
            beam.rays[i,17] = Ez    # Ep



        beam_out = ShadowBeam(beam=beam)

        beam_out.history.append(ShadowOEHistoryItem()) # fake Source
        beam_out._oe_number = 0

        # just to create a safe history for possible re-tracing
        beam_out.traceFromOE(beam_out, self.create_dummy_oe(), history=True)

        #self.send("Beam", beam_out)

        return beam_out




if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    a = QApplication(sys.argv)
    ow = ShadowConverter()
    ow.show()
    a.exec_()
    ow.saveSettings()


