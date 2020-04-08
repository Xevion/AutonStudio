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
        config.titleEvent, config.titleValues = titleWindow.read()
        logger.debug(f'TitleWindow Event Received: {config.titleEvent}')

        # Allows the application to exit. A 'None' event is sent when the Close Button is pressed by the User.
        # Could also be sent by a erroneous or invalid event, possibly.
        if config.titleEvent is None:
            logger.critical('Exit/Invalid event received. Application is exiting.')
            break

        # Activate the Configuration Window
        if not config.configActive and config.titleEvent == TitleEvents.CONFIG_BUTTON:
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

            # Draw basic elements on the Canvas
            canvas.draw_rectangle([2, 2], [348, 348], line_color='black', line_width=5)
            canvas.draw_line([13, 20], [337, 20], color='black', width=2)  # 18 pixels is one inch
            canvas.draw_text('18 in.', [162, 13], color='black', font='Verdana 7 bold')
            configRectangle = None  # We keep this variable available so that we can edit it multiple times.

            # Mainloop for Configuration Window
            while config.configActive:
                config.configEvent, config.configValues = configWindow.read()
                logger.debug(f'ConfigWindow Event Received: {config.configEvent}')

                # Logic for Invalid Event/Close/Back button
                if config.configEvent is None or config.configEvent == ConfigEvents.CONFIG_BACK_BUTTON:
                    logger.debug('Exit/Invalid event received. ConfigWindow is exiting.')
                    config.configActive = False
                    titleWindow.UnHide()
                    configWindow.Close()
                    break

                # Logic for 'Goto Studio' button in Configuration Window
                if config.configEvent == ConfigEvents.GOTO_STUDIO_BUTTON:
                    logger.debug('Goto Studio button received, leaving ConfigWindow.')
                    config.studioActive = False
                    configWindow.Close()
                    config.configActive = False
                    config.titleEvent = TitleEvents.CONTINUE_BUTTON
                    break

                # Ensure that the combo boxes only allow digits and dots of proper notation.
                # if configEvent == ConfigEvents.ROBOT_SIZE_X:
                #     get = manage.Helper.getDigits(configValues[configEvent])
                #     optionsTab[6][0].update(get[0])
                # elif configEvent == ConfigEvents.ROBOT_SIZE_Y:
                #     optionsTab[6][2].update(manage.Helper.getDigits(configValues[configEvent])[0])

                if config.configEvent == ConfigEvents.UPDATE_CONFIG:
                    logger.debug('Updating Robot Rectangle Configuration')
                    x, y = config.configValues[ConfigEvents.ROBOT_SIZE_X], config.configValues[ConfigEvents.ROBOT_SIZE_Y]
                    # Use a try statement to parse the values within the two fields
                    try:
                        x, y = float(x), float(y)
                        if x <= 0 or y <= 0:
                            raise InvalidRobotDimensions()

                        x = int(config.configValues[ConfigEvents.ROBOT_SIZE_X]) * 18
                        y = int(config.configValues[ConfigEvents.ROBOT_SIZE_Y]) * 18
                        config.size = (x, y)

                        # Redrawing the figure
                        if configRectangle is not None:
                            logger.debug('Deleting Robot Rectangle Preview from Canvas')
                            canvas.delete_figure(configRectangle)

                        configRectangle = canvas.draw_rectangle(
                            [173 - x / 2, 173 + y / 2],
                            [173 + x / 2, 173 - y / 2],
                            line_width=3
                        )
                        optionsTab[4][0].update(value='Custom')
                    except ValueError:
                        logger.error(f'Invalid Robot Dimensions Received: ({x}, {y})')

                # Field Configuration handling
                if config.configEvent == ConfigEvents.FIELD_DD:
                    logger.debug('Updating Field Configuration')
                    config.fieldConfiguration = config.configValues[ConfigEvents.FIELD_DD]

        # Start running Studio Window
        if config.titleEvent == TitleEvents.CONTINUE_BUTTON:
            logger.debug('Opening Studio Window')


if __name__ == "__main__":
    main()
