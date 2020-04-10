"""
This file contains models helpful with managing data and configuration values within the application.
Hopefully, most of the raw logic and calculations will be placed here in order to abstract parts of the GUI away,
and allow for a overall simpler to debug and manage application.
"""
import math
import re

from PySimpleGUI import Graph

from autonstudio import exceptions


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

        # large list of proprietary 'global' mimic vars
        # ultimate goal is complete removal of these
        self.points = []  # A list of points representing the paths the robot takes in AutonStudio.
        self.turns = []
        self.velocities = []
        self.defaultVelocity = 48
        self.point_lines = []
        self.turn_circles = []
        self.convertedPoints = []
        self.turnIndicator_circles = []
        self.turnIndicator_text = []
        self.selectedPathNum = None
        self.selectedTurnNum = None
        self.startHeading = 0.0
        self.configRobot_rectangle = None
        self.selectedOperation = None
        self.pathEditUpdated = False
        self.turnEditUpdated = False
        self.startPoint_circle = None
        self.startPoint_line = None
        self.robot_rectangle = None
        self.robot_point = None
        self.robot_polygon = None
        self.delete_point_circles = []
        self.delete_turn_circles = []
        self.pathStrings = [None]
        self.turnStrings = [None]

        # Variables managing window events/values
        # Stored here for cross-window access
        self.titleEvent, self.titleValues = None, None
        self.configEvent, self.configValues = None, None
        self.studioEvent, self.studioValues = None, None

        # Variables used for tracking points
        self.ppoints = []


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

    @staticmethod
    def generate_path_string(p1, p2, velocity, heading):
        return f'({p1[0]}, {p1[1]}) to ({p2[0]}, {p2[1]}) going {velocity} in/s at {heading}°'

    @staticmethod
    def generate_turn_string(turn, points):
        return f'Turn to {turn[1]} ° at ({points[turn[0]][0]}, {points[turn[0]][1]})'

    @staticmethod
    def convert_coordinates_to_inches(points, pixels_per_inch, field_length_inches):
        converted_points = []
        for p in points:
            new_point = [None, None]
            new_point[0] = p[0] / pixels_per_inch
            new_point[1] = p[1] / pixels_per_inch
            new_point[0] -= (field_length_inches / 2.0)
            new_point[1] -= (field_length_inches / 2.0)
            new_point[0] = round(new_point[0], 2)
            new_point[1] = round(new_point[1], 2)
            converted_points.append(new_point)
        return converted_points

    @staticmethod
    def convert_coordinates_to_pixels(points, pixels_per_inch, field_length_pixels):
        converted_points = []
        for p in points:
            new_point = [None, None]
            new_point[0] = p[0] * pixels_per_inch
            new_point[1] = p[1] * pixels_per_inch
            new_point[0] += (field_length_pixels / 2.0)
            new_point[1] += (field_length_pixels / 2.0)
            new_point[0] = round(new_point[0], 2)
            new_point[1] = round(new_point[1], 2)
            converted_points.append(new_point)
        return converted_points

    @staticmethod
    def calculate_movement_per_frame(point1, point2, inches_per_second, frames_per_second, pixels_per_inch):
        pixels_per_frame = (inches_per_second * pixels_per_inch) / frames_per_second
        if point2[0] - point1[0] == 0:
            x_per_frame = 0
            y_per_frame = pixels_per_frame
        elif point2[1] - point1[1] == 0:
            x_per_frame = pixels_per_frame
            y_per_frame = 0
        else:
            x_to_y_ratio = (point2[0] - point1[0]) / (point2[1] - point1[1])
            y_per_frame = math.sqrt(pixels_per_frame ** 2 / (x_to_y_ratio ** 2 + 1))  # Uses derived formula
            x_per_frame = x_to_y_ratio * y_per_frame
        if point2[1] <= point1[1]:
            y_per_frame *= -1
            x_per_frame *= -1
        if point2[0] > point1[0] and y_per_frame == 0.0:
            x_per_frame *= -1
        return [x_per_frame, y_per_frame]

    @staticmethod
    def clean_coordinates(coord=''):
        string = ''.join(c for c in coord if c.isdigit() or c == '.' or c == '-')
        if len(string) > 0 and (string[0] == '.'):
            string = string[1:-1]
        if len(string) > 0 and (string[-1] == '.' or string[-1] == '-'):
            string = string[0:-1]
        if len(string) == 0:
            string += '0'
        return string

    @staticmethod
    def sort_turns(turns):
        if len(turns) > 0:
            sorted_turns = [turns[0]]
            for t in turns:
                if t is turns[0]:
                    continue
                for st in sorted_turns:
                    if t[0] < st[0]:
                        sorted_turns.insert(0, t)
                        break
                if not sorted_turns.__contains__(t):
                    sorted_turns.append(t)
            return sorted_turns
        return turns

    @staticmethod
    def calculate_rotation_per_frame(points, angle1, angle2, degrees_per_second, frames_per_second):
        deltas = []
        degrees_per_frame = degrees_per_second / frames_per_second
        for p in points:
            point_deltas = [[], []]
            delta_angle = float(angle2) - float(angle1)
            frame_count = abs(int(delta_angle / degrees_per_frame))
            current_angle = float(angle1)
            for i in range(0, frame_count):
                current_angle += degrees_per_frame * math.copysign(1.0, delta_angle)
                # Use clockwise rotation matrix
                point_deltas[0].append(
                    p[0] * math.sin(math.radians(current_angle)) + p[1] * math.cos(math.radians(current_angle)))
                point_deltas[1].append(
                    p[0] * math.cos(math.radians(current_angle)) - p[1] * math.sin(math.radians(current_angle)))
                # if i == frame_count - 1:  # Account for uneven division of degrees into frames
                # angle2 = float(angle2)
                # point_deltas[0][i] = (p[0]*math.sin(math.radians(angle2-current_angle)) + p[1]*math.cos(math.radians(angle2-current_angle)))
                # point_deltas[1][i] = p[0]*(math.cos(math.radians(angle2-current_angle)) - p[1]*math.sin(math.radians(angle2-current_angle)))
            deltas.append(point_deltas)
        return deltas


class Point(object):
    """
    A advanced class that manages points along a path built inside AutonStudio.
    Manages field rendering, assists with calculations, text generation and more.
    """

    def __init__(self, x: int, y: int, i: int):
        # basic Point attributes
        self.x, self.y, self.index, self.turn, self.velocity = x, y, i, 0.0, 42

        # rendering attributes
        self.deleteMarker = None
        self.turnIndicator = None

    def render(self, field: Graph, action: None) -> None:
        """
        Renders the point (and associated turns) on the field, deleting it if it was rendered.
        :param field: A field object.
        :param action: The current action being taken by the User inside the Studio.
        """
        pass

    def rotationScheme(self, angle: float, dps: int = 0, fps: int = 60):
        """

        :param angle: the angle the point should end upon.
        :param dps: degrees per second
        :param fps: frames per second
        :return: A list of points
        """

    def getPathstring(self, other) -> str:
        """
        Generates a string for the GUI to use in the Paths List.

        :param other: The next point in the list.
        :return: A string explaining the path taken between two points.
        """
        return f'({self.x}, {self.y}) to ({other.x}, {other.y}) going {self.velocity} in/s at {self.turn}°'

    def getTurnstring(self) -> str:
        """
        Generates a Turn String if a turn is being made. Otherwise raises an exception.
        :return: A string explaining the turn being taken at this point.
        """
        if self.turn is not None:
            return f'Turn to {self.turn} ° at ({self.x}, {self.y})'
        else:
            raise exceptions.NoPointTurning(f'Point #{self.index + 1} does not turn.')

    def isClicked(self, x, y):
        """
        A simple helper function that helps to determine whether a point has been clicked.

        :param x: X coordinate of the spot clicked on the Field.
        :param y: Y coordinate of the spot clicked on the Field.
        :return: A boolean that is true if the Point has been clicked.
        """
        return abs(x - self.x) < 10 and abs(y - self.y) < 10

    def __repr__(self):
        return f'Path({self.x}, {self.y})'
