import logging

import PySimpleGUI as pygui

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window

from autonstudio.enums import TitleEvents

def main() -> None:
    """
    The mainloop for the entire application, taking in events and processing GUI logic.
    """

    pygui.theme('Dark Green')
    menu_column = [
        [Text('\n\n')],
        [Button('Click to Continue to Studio', key=TitleEvents.CONTINUE_BUTTON, font='verdana')],
        [Button('Add Configuration', key=TitleEvents.CONFIG_BUTTON, font='Verdana')],
        [Listbox(
            [
                'Mechanum with Odometry',
                'Mechanum without Odometry',
                'H-Drive with Odometry',
                'H-Drive without Odometry'
            ],
            enable_events=True, key=TitleEvents.SELECT_DRIVETRAIN, size=(25, 4),
            default_values='Mechanum with Odometry', font='verdana'
        )]
    ]
    titleLayout = [
        [Text('Welcome to Auton Studio', text_color='Black', font='Verdana 20 bold', justification='center',
                   size=[32, 1])],
        [Image('resources/autonStudioLogo.png'), Column(menu_column)],
    ]
    titleWindow = Window('Auton Studio', titleLayout)

    while True:
        titleEvent, titleValues = titleWindow.read()

if __name__ == "__main__":
    main()