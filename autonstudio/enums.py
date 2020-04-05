"""
This file organizes all Enum classes.
These classes help with organizing GUI Widget events into a simple space, allowing finer, more explicit control
in a refined and Pythonic method.
"""

from enum import Enum


class TitleEvents(Enum):
    """
    A Enum class representing Event keys for PySimpleGUI.
    """

    SELECT_DRIVETRAIN = 'SELECT_DRIVETRAIN'
    CONTINUE_BUTTON = 'CONTINUE_BUTTON'
    CONFIG_BUTTON = 'CONFIG_BUTTON'
