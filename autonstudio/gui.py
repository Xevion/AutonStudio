"""
This file controls all GUI operations, and acts as the heart of the program with a crude PySimpleGUI interface.
"""

import logging

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window, Combo, Graph, InputText, theme

from autonstudio import manage
from autonstudio.enums import TitleEvents

logging.basicConfig(
    format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s] %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger('gui')
logger.setLevel(logging.DEBUG)


def main() -> None:
    """
    The mainloop for the entire application, taking in events and processing GUI logic.
    """

    theme('Dark Green')
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
    logger.info('TitleWindow is prepared, Application starting shortly.')
    config = manage.Config()

    while True:
        titleEvent, titleValues = titleWindow.read()
        logger.debug(f'Event Received: {titleEvent}')

        # Allows the application to exit. A 'None' event is sent when the Close Button is pressed by the User.
        # Could also be sent by a erroneous or invalid event, possibly.
        if titleEvent is None:
            logger.critical('Exit/Invalid event received. Application is exiting.')
            break

        if not config.configActive and titleEvent == TitleEvents.CONFIG_BUTTON:
            config.ConfigWindow = True

            canvas = Graph(canvas_size=[300, 300], graph_bottom_left=[0, 0], graph_top_right=[350, 350],
                           background_color=None, key='-CANVAS-', enable_events=True)

            optionsTab = [
                [Text('\n' * 3)],
                [Button('Add Servo', key='-ADD_SERVO_BUTTON-', font='verdana')],
                [Button('Add Hex Core Motor', key='-ADD_HEX_CORE_BUTTON-', font='verdana')],
                [Text('Select Field Configuration', font='verdana')],
                [Combo(['FTC Skystone', 'FTC Rover Ruckus', 'None'], enable_events=True, key='-FIELD_DD-'
                       , default_value=fieldConfiguration, font='verdana')],
                [Text('\nInput Robot Size in Inches (X by Y)', font='verdana')],
                [InputText(enable_events=True, size=[4, 1], key='-ROBOT_SIZE_X-', font='verdana'),
                 Text('by', font='verdana'),
                 InputText(enable_events=True, size=[4, 1], key='-ROBOT_SIZE_Y-', font='verdana')],
                [Text('\n' * 8), Button('Update', key='-UPDATE_CONFIG-', bind_return_key=True, font='verdana')]]

            configLayout = [
                [canvas, Column(optionsTab)],
                [Button("Back", key='-CONFIG_BACK_BUTTON-', font='verdana'),
                 Button('Go to Studio', key='-GOTO_STUDIO_BUTTON-', font='verdana')]
            ]

            configWindow = Window('Configuration Menu', configLayout)
            configWindow.finalize()

            canvas.draw_rectangle([2, 2], [348, 348], line_color='black', line_width=5)
            canvas.draw_line([13, 20], [337, 20], color='black', width=2)  # 18 pixels is one inch
            canvas.draw_text('18 in.', [162, 13], color='black', font='Verdana 7 bold')

            while True and configWindowActive:
                eventC, valuesC = configWindow.Read()

                if eventC is None or eventC == '-CONFIG_BACK_BUTTON-':
                    configWindowActive = False
                    titleWindow.UnHide()
                    configWindow.Close()
                    break

                if eventC == '-GOTO_STUDIO_BUTTON-':
                    studioWindowActive = False
                    configWindow.Close()
                    configWindowActive = False
                    event0 = '-CONTINUE_BUTTON-'
                    break

                if eventC == '-UPDATE_CONFIG-' and valuesC['-ROBOT_SIZE_X-'] != '' and valuesC['-ROBOT_SIZE_Y-'] != '':
                    if configRobot_rectangle is not None:
                        canvas.delete_figure(configRobot_rectangle)
                    robotSize_X = int(valuesC['-ROBOT_SIZE_X-']) * 18
                    robotSize_Y = int(valuesC['-ROBOT_SIZE_Y-']) * 18
                    configRobot_rectangle = canvas.draw_rectangle([173 - robotSize_X / 2, 173 + robotSize_Y / 2],
                                                                  [173 + robotSize_X / 2, 173 - robotSize_Y / 2],
                                                                  line_width=3)

                if eventC == '-FIELD_DD-':
                    fieldConfiguration = valuesC['-FIELD_DD-']


if __name__ == "__main__":
    main()
