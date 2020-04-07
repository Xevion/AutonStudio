"""
This file controls all GUI operations, and acts as the heart of the program with a crude PySimpleGUI interface.
"""

import logging

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window, Combo, Graph, InputText, theme

from autonstudio import manage
from autonstudio.enums import TitleEvents, ConfigEvents
from autonstudio.exceptions import InvalidRobotDimensions

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
        logger.debug(f'TitleWindow Event Received: {titleEvent}')

        # Allows the application to exit. A 'None' event is sent when the Close Button is pressed by the User.
        # Could also be sent by a erroneous or invalid event, possibly.
        if titleEvent is None:
            logger.critical('Exit/Invalid event received. Application is exiting.')
            break

        if not config.configActive and titleEvent == TitleEvents.CONFIG_BUTTON:
            config.configActive = True

            canvas = Graph(canvas_size=[300, 300], graph_bottom_left=[0, 0], graph_top_right=[350, 350],
                           background_color=None, key=ConfigEvents.CANVAS, enable_events=True)

            optionsTab = [
                [Text('\n' * 3)],
                [Button('Add Servo', key=ConfigEvents.ADD_SERVO_BUTTON, font='verdana')],
                [Button('Add Hex Core Motor', key=ConfigEvents.ADD_HEX_CORE_BUTTON, font='verdana')],
                [Text('Select Field Configuration', font='verdana')],
                [Combo(['FTC Skystone', 'FTC Rover Ruckus', 'None'], enable_events=True, key=ConfigEvents.FIELD_DD,
                       default_value=config.fieldConfiguration, font='verdana')],
                [Text('\nInput Robot Size in Inches (X by Y)', font='verdana')],
                [InputText(enable_events=True, size=[4, 1], key=ConfigEvents.ROBOT_SIZE_X, font='verdana'),
                 Text('by', font='verdana'),
                 InputText(enable_events=True, size=[4, 1], key=ConfigEvents.ROBOT_SIZE_Y, font='verdana')],
                [Text('\n' * 8), Button('Update', key=ConfigEvents.UPDATE_CONFIG, bind_return_key=True, font='verdana')]]

            configLayout = [
                [canvas, Column(optionsTab)],
                [Button('Back', key=ConfigEvents.CONFIG_BACK_BUTTON, font='verdana'),
                 Button('Go to Studio', key=ConfigEvents.GOTO_STUDIO_BUTTON, font='verdana')]
            ]

            configWindow = Window('Configuration Menu', configLayout)
            configWindow.finalize()

            canvas.draw_rectangle([2, 2], [348, 348], line_color='black', line_width=5)
            canvas.draw_line([13, 20], [337, 20], color='black', width=2)  # 18 pixels is one inch
            canvas.draw_text('18 in.', [162, 13], color='black', font='Verdana 7 bold')
            configRectangle = None

            # Mainloop for Configuration Window
            while config.configActive:
                configEvent, configValues = configWindow.Read()
                logger.debug(f'ConfigWindow Event Received: {configEvent}')

                # Logic for Invalid Event/Close/Back button
                if configEvent is None or configEvent == ConfigEvents.CONFIG_BACK_BUTTON:
                    logger.debug('Exit/Invalid event received. ConfigWindow is exiting.')
                    config.configActive = False
                    titleWindow.UnHide()
                    configWindow.Close()
                    break

                # Logic for 'Goto Studio' button in Configuration Window
                if configEvent == ConfigEvents.GOTO_STUDIO_BUTTON:
                    logger.debug('Goto Studio button received, leaving ConfigWindow.')
                    config.studioActive = False
                    configWindow.Close()
                    config.configActive = False
                    titleEvent = TitleEvents.CONTINUE_BUTTON
                    break

                if configEvent == ConfigEvents.UPDATE_CONFIG:
                    logger.debug('Updating Robot Rectangle Configuration')
                    x, y = configValues[ConfigEvents.ROBOT_SIZE_X], configValues[ConfigEvents.ROBOT_SIZE_Y]
                    # Use a try statement to parse the values within the two fields
                    try:
                        x, y = float(x), float(y)
                        if x <= 0 or y <= 0:
                            raise InvalidRobotDimensions(x=x, y=y)
                        robotSize_X = int(configValues[ConfigEvents.ROBOT_SIZE_X]) * 18
                        robotSize_Y = int(configValues[ConfigEvents.ROBOT_SIZE_Y]) * 18

                        if configRectangle is not None:
                            configRectangle.delete_figure()

                        configRectangle = canvas.draw_rectangle(
                            [173 - robotSize_X / 2, 173 + robotSize_Y / 2],
                            [173 + robotSize_X / 2, 173 - robotSize_Y / 2],
                            line_width=3
                        )
                    except ValueError:
                        logger.error(f'Invalid Robot Dimensions Received: ({x}, {y})')

                # Field Configuration handling
                if configEvent == ConfigEvents.FIELD_DD:
                    logger.debug('Updating Field Configuration')
                    config.fieldConfiguration = configValues[ConfigEvents.EVENT_DD]


if __name__ == "__main__":
    main()
