"""
This file contains models helpful with managing data and configuration values within the application.
Hopefully, most of the raw logic and calculations will be placed here in order to abstract parts of the GUI away,
and allow for a overall simpler to debug and manage application.
"""

class Config(object):
    """
    A relatively simple class that assists with configuration values within the application.
    Should also help load and save application states, when implemented.
    """

    def __init__(self):
