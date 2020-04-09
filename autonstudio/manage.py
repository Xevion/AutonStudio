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
        self.studioActive = False  # Whether or not the Studio Window is active.
        self.configActive = False  # Whether or not the Config Window is active.
        self.fieldConfiguration = 'None'  # Field configuration name
        self.size = None  # Size of the robot
        self.drivetrain = 'Mechanum with Odometry'
        self.fieldInstance = None  # Field Instance for saving while leaving Studio Window temporarily
        self.hiddenStudio = False  # Whether or not the Studio Window is hidden temporarily

        self.titleEvent, self.titleValues = None, None
        self.configEvent, self.configValues = None, None


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

        :param string: A string containing regular notation integers and/or decimals.
        :return: The numbers in string format in a list.
        """
        return re.findall(Helper.digits, string)

