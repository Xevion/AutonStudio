"""
This file contains exceptions used by the application.
Exceptions are kept here for better readability within the primary application files,
as well as for proper organization within a well abstracted application.
Custom Exceptions are made to better handle errors made by users while they use the application.
"""


class InvalidRobotDimensions(ValueError):
    """
    Raised whenever a User inputs invalid dimensions for a robot.

    Valid Dimensions (x & y): (0,]
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def stringify(self):
        return ', '.join(f'{k}:{v}' for k,v in self.kwargs.items())

    def __repr__(self):
        return f'InvalidRobotDimensions({self.stringify()})'
