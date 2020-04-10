"""
This file contains models helpful with managing data and configuration values within the application.
Hopefully, most of the raw logic and calculations will be placed here in order to abstract parts of the GUI away,
and allow for a overall simpler to debug and manage application.
"""

import re

from PySimpleGUI import Graph


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

        self.points = []  # A list of points representing the paths the robot takes in AutonStudio.
        self.turns = []
        self.velocities = []
        self.defaultVelocity = 48
        self.point_lines = []
        self.turn_circles = []
        self.convertedPoints = []
        self.turnIndicator_circles = []
        self.turnIndicator_text = []

        self.titleEvent, self.titleValues = None, None
        self.configEvent, self.configValues = None, None
        self.studioEvent, self.studioValues = None, None


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


class Point(object):
    """
    A advanced class that manages points along a path built inside AutonStudio.
    Manages field rendering, assists with calculations, text generation and more.
    """

    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
        self.turn = None

    def render(self, field: Graph, action: None) -> None:
        """
        Renders the point (and associated turns) on the field, deleting it if it was rendered.
        :param field: A field object.
        :param action: The current action being taken by the User inside the Studio.
        """
        pass

    def __repr__(self):
        return f'Path({self.x}, {self.y})'
