"""
This file contains models helpful with managing data and configuration values within the application.
Hopefully, most of the raw logic and calculations will be placed here in order to abstract parts of the GUI away,
and allow for a overall simpler to debug and manage application.
"""

import re


class Config(object):
    """
    A relatively simple class that assists with configuration values within the application.
    Should also help load and save application states, when implemented.
    """

    def __init__(self):
        self.configActive = False  # Whether or not the Config Window is active.
        self.fieldConfiguration = 'None'


class Helper(object):
    """
    A simple class designed to store helper methods, like number strippers or basic calculations.
    Not to be instantiated. Static methods only.
    """

    digits = re.compile("\d+(?:\.\d+)")

    @staticmethod
    def getDigits(string):
        """
        Returns digits from a string. Ignores letters and spacing, regular notation numbers accepted only.

        :param string: A string containing regular nontation integers and/or decimals.
        :return: The numbers in string format in a list.
        """
        return re.findall(Helper.digits, string)

