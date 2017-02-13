__author__ = 'srio'
import sys
import numpy

from oasys.widgets import widget

from orangewidget import  gui
from PyQt4 import QtGui

from crystalpy.util.PolarizedPhotonBunch import PolarizedPhotonBunch
from crystalpy.util.PolarizedPhoton import PolarizedPhoton
from crystalpy.util.Vector import Vector
from crystalpy.util.StokesVector import StokesVector

from orangecontrib.shadow.util.shadow_objects import ShadowBeam, EmittingStream, TTYGrabber
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot

import Shadow
from orangecontrib.shadow.util.shadow_objects import ShadowBeam, ShadowOpticalElement, ShadowOEHistoryItem


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



def fromArray():


    npoint = 1000
    vx = numpy.zeros(npoint) + 0.0
    vy = numpy.zeros(npoint) + 1.0
    vz = numpy.zeros(npoint) + 0.0

    s0 = numpy.zeros(npoint) + 1
    s1 = numpy.zeros(npoint) + 0
    s2 = numpy.zeros(npoint) + 1
    s3 = numpy.zeros(npoint) + 0

    energy = numpy.zeros(npoint) + 3000.0

    photon_bunch = PolarizedPhotonBunch([])


    photons_list = list()
    for i in range(npoint):

        photon = PolarizedPhoton(energy_in_ev=energy[i],
                                 direction_vector=Vector(vx[i],vy[i],vz[i]),
                                 stokes_vector=StokesVector([s0[i],s1[i],s2[i],s3[i]]))
        #photon_bunch.add(photon)
        photons_list.append(photon)


    photon_bunch.add(photons_list)

    return photon_bunch

def create_dummy_oe():
    empty_element = ShadowOpticalElement.create_empty_oe()

    # empty_element._oe.DUMMY = self.workspace_units_to_cm

    empty_element._oe.T_SOURCE     = 0.0
    empty_element._oe.T_IMAGE = 0.0
    empty_element._oe.T_INCIDENCE  = 0.0
    empty_element._oe.T_REFLECTION = 180.0
    empty_element._oe.ALPHA        = 0.0

    empty_element._oe.FWRITE = 3
    empty_element._oe.F_ANGLE = 0

    return empty_element

def from_photon_bunch_to_shadow():

    # self.array_dict["number of photons"] = i
    # self.array_dict["energies"] = energies
    # self.array_dict["deviations"] = deviations
    # self.array_dict["s0"] = stokes[0, :]
    # self.array_dict["s1"] = stokes[1, :]
    # self.array_dict["s2"] = stokes[2, :]
    # self.array_dict["s3"] = stokes[3, :]
#     self.array_dict["polarization degree"] = polarization_degrees
#
#
# def get_array(self, key):

    photon_beam = fromArray() # self.incoming_bunch

    N =        photon_beam.get_array("number of photons")
    energies = photon_beam.get_array("energies")
    S0 =       photon_beam.get_array("s0")
    S1 =       photon_beam.get_array("s1")
    S2 =       photon_beam.get_array("s2")
    S3 =       photon_beam.get_array("s3")

    beam = Shadow.Beam(N)

    for i in range(N):
        s0 = S0[i]
        s1 = S1[i]
        s2 = S2[i]
        s3 = S3[i]


        if (s1**2 + s2**2 + s3**2 < s0**2):
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

        delta = numpy.arcsin( numpy.sqrt(sin2delta) )

        beam.rays[:,9] = Ex
        beam.rays[:,10] = 0.0
        beam.rays[:,11] = 0.0
        beam.rays[:,12] = 0.0
        beam.rays[:,13] = delta
        beam.rays[:,14] = 0.0
        beam.rays[:,15] = 0.0
        beam.rays[:,16] = Ez

        # add directions
        # add energies



    beam_out = ShadowBeam()
    # beam_out.loadFromFile(self.beam_file_name)
    beam_out.setBeam(beam)
    beam_out.history.append(ShadowOEHistoryItem()) # fake Source
    beam_out._oe_number = 0

    # just to create a safe history for possible re-tracing
    beam_out.traceFromOE(beam_out, create_dummy_oe(), history=True)

    # self.send("Beam", beam_out)





if __name__ == "__main__":
    # a = QtGui.QApplication(sys.argv)
    # ow = ShadowConverter()
    # ow.show()
    # a.exec_()
    # ow.saveSettings()

    # a = from_photon_bunch_to_shadow()
    pass

