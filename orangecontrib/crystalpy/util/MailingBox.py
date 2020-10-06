"""
Contains the data that are sent by the crystal diffraction widget to the viewer.
"""


class MailingBox(object):
    def __init__(self, diffraction_result, mueller_result):
        self.diffraction_result = diffraction_result
        self.mueller_result = mueller_result
