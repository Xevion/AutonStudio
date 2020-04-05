"""
This file organizes all Enum classes.
These classes help with organizing GUI Widget events into a simple space, allowing finer, more explicit control
in a refined and Pythonic method.
"""

from enum import Enum


class TitleEvents(Enum):
    """
    A Enum class containing Event keys used by the Title Window.
    """

    SELECT_DRIVETRAIN = 'SELECT_DRIVETRAIN'
    CONTINUE_BUTTON = 'CONTINUE_BUTTON'
    CONFIG_BUTTON = 'CONFIG_BUTTON'


class ConfigEvents(Enum):
    """
    A Enum class containing Event keys used by the Configuration Window.
    """

    CANVAS = 'CANVAS'

    ADD_SERVO_BUTTON = 'ADD_SERVO_BUTTON'
    ADD_HEX_CORE_BUTTON = 'ADD_HEX_CORE_BUTTON'
    FIELD_DD = 'FIELD_DD'

    ROBOT_SIZE_X = 'ROBOT_SIZE_X'
    ROBOT_SIZE_Y = 'ROBOT_SIZE_Y'

    UPDATE_CONFIG = 'UPDATE_CONFIG'
    CONFIG_BACK_BUTTON = 'CONFIG_BACK_BUTTON'
    GOTO_STUDIO_BUTTON = 'GOTO_STUDIO_BUTTON'
