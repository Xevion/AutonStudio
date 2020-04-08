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


class StudioEvents(Enum):
    """
    A Enum class containing Event keys used by the Studio Window.
    """

    PATH_INFO = 'PATH_INFO'
    TURN_INFO = 'TURN_INFO'
    SAVE_INFO = 'SAVE_INFO'

    FIELD = 'FIELD'

    PATH_LIST = 'PATH_LIST'
    EDIT_PATH_BUTTON = 'EDIT_PATH_BUTTON'
    ROUND_ALL_BUTTON = 'ROUND_ALL_BUTTON'

    START_X_TEXT = 'START_X_TEXT'
    START_Y_TEXT = 'START_Y_TEXT'
    START_X_INPUT = 'START_X_INPUT'
    START_Y_INPUT = 'START_Y_INPUT'

    FINAL_X_TEXT = 'FINAL_X_TEXT'
    FINAL_Y_TEXT = 'FINAL_Y_TEXT'
    FINAL_X_INPUT = 'FINAL_X_INPUT'
    FINAL_Y_INPUT = 'FINAL_Y_INPUT'

    VELOCITY_INPUT = 'VELOCITY_INPUT'
    DESELECT_BUTTON = 'DESELECT_BUTTON'

    TURN_LIST = 'TURN_LIST'
    EDIT_TURN_BUTTON = 'EDIT_TURN_BUTTON'
    ANGLE_TEXT = 'ANGLE_TEXT'
    ANGLE_INPUT = 'ANGLE_INPUT'

    SAVES_LIST = 'SAVES_LIST'
    SELECT_SAVE_BUTTON = 'SELECT_SAVE_BUTTON'

    SAVE_BUTTON = 'SAVE_BUTTON'
    LOAD_BUTTON = 'LOAD_BUTTON'
    START_POINT_BUTTON = 'START_POINT_BUTTON'
    ADD_POINT_BUTTON = 'ADD_POINT_BUTTON'
    DELETE_POINT_BUTTON = 'DELETE_POINT_BUTTON'
    ADD_TURN_BUTTON = 'ADD_TURN_BUTTON'
    DELETE_TURN_BUTTON = 'DELETE_TURN_BUTTON'
    SIMULATE_BUTTON = 'SIMULATE_BUTTON'
    CLEAR_FIELD_BUTTON = 'CLEAR_FIELD_BUTTON'
    EXPORT_BUTTON = 'EXPORT_BUTTON'

    BACK_BUTTON = 'BACK_BUTTON'
    GOTO_CONFIG_BUTTON = 'GOTO_CONFIG_BUTTON'