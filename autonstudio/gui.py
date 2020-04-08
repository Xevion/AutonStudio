"""
This file controls all GUI operations, and acts as the heart of the program with a crude PySimpleGUI interface.
"""

import logging

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window, Combo, Graph, InputText, Tab, TabGroup, theme

from autonstudio import manage
from autonstudio.enums import TitleEvents, ConfigEvents, StudioEvents
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
        if config.titleEvent == TitleEvents.CONTINUE_BUTTON and not config.studioActive:
            logger.debug('Opening Studio Window')

            config.studioActive = True
            titleWindow.hide()

            pathInfo = Text('None', key=StudioEvents.PATH_INFO, size=[20, 1], font='verdana')
            turnInfo = Text('None', key=StudioEvents.TURN_INFO, size=[20, 1], font='verdana')
            savesInfo = Text('None', key=StudioEvents.SAVE_INFO, size=[20, 1], font='verdana')

            # Each inch is five pixels
            field = Graph(canvas_size=[720, 720], graph_bottom_left=[0, 0], graph_top_right=[720, 720],
                             background_color='#BAB8B8', key=StudioEvents.FIELD, enable_events=True)
            fieldSave_MASTER = field

            paths_tab = [[Listbox(values=[], size=(50, 6), key=StudioEvents.PATH_LIST)],
                         [Button('Edit Path', key=StudioEvents.EDIT_PATH_BUTTON, font='verdana'),
                          Button('Round All', key=StudioEvents.ROUND_ALL_BUTTON, font='verdana')],
                         [Text('Selected Path:', font='verdana'), pathInfo],
                         [Text('Start X', key=StudioEvents.START_X_TEXT, font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.START_X_INPUT, font='verdana'),
                          Text('   Start Y', key=StudioEvents.START_Y_TEXT, font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.START_Y_INPUT, font='verdana')],
                         [Text('Final X', key=StudioEvents.FINAL_X_TEXT, font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.FINAL_X_INPUT, font='verdana'),
                          Text('   Final Y', key=StudioEvents.FINAL_Y_TEXT, font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.FINAL_Y_INPUT, font='verdana')],
                         [Text('Velocity', font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.VELOCITY_INPUT, font='verdana')],
                         [Button('Deselect', key=StudioEvents.DESELECT_BUTTON, font='verdana')]]

            turns_tab = [[Listbox(values=[], size=(50, 6), key=StudioEvents.TURN_LIST, font='verdana')],
                         [Button('Edit Turn', key=StudioEvents.EDIT_TURN_BUTTON, font='verdana')],
                         [Text('Selected Turn:', font='verdana'), turnInfo],
                         [Text('Angle', key=StudioEvents.ANGLE_TEXT, font='verdana'),
                          InputText(enable_events=True, size=[10, 1], key=StudioEvents.ANGLE_INPUT, font='verdana')]]

            saves_tab = [[Listbox(values=[], size=(50, 4), key=StudioEvents.SAVES_LIST, font='verdana')],
                         [Button('Select Save', key=StudioEvents.SELECT_SAVE_BUTTON, font='verdana')],
                         [Text('Selected Turn:', font='verdana')]]

            editing_tabGroup = TabGroup(
                layout=[[Tab(layout=paths_tab, title='Paths', font='Verdana'),
                         Tab(layout=turns_tab, title='Turns', font='Verdana 10 bold')]])

            saves_tabGroup = TabGroup(layout=[[Tab(layout=saves_tab, title='Saves')]])

            main_column = [[Button('Save Field', key=StudioEvents.SAVE_BUTTON, font='verdana'),
                            Button('Load Field', key=StudioEvents.LOAD_BUTTON, font='verdana')],
                           [Button('Set Start Point', key=StudioEvents.START_POINT_BUTTON, font='verdana')],
                           [Button('Add Point', key=StudioEvents.ADD_POINT_BUTTON, font='verdana'),
                            Button('Delete Point', key=StudioEvents.DELETE_POINT_BUTTON, font='verdana')],
                           [Button('Add Turn', key=StudioEvents.ADD_TURN_BUTTON, font='verdana'),
                            Button('Delete Turn', key=StudioEvents.DELETE_TURN_BUTTON, font='verdana')],
                           [Button('Add Robot Operation', font='verdana')],
                           [Button('Simulate Robot Run', key=StudioEvents.SIMULATE_BUTTON, font='verdana')],
                           [Text('\nEdit Menu:', font='verdana')],
                           [editing_tabGroup],
                           [Text(
                               f'Selected Drivetrain: {config.drivetrain}',
                               font='verdana')],
                           [Button('Clear Field', key=StudioEvents.CLEAR_FIELD_BUTTON, font='verdana')],
                           [Button('Export Field', key=StudioEvents.EXPORT_BUTTON, font='verdana')]]

            layout = [[Text(f'Field Configuration: {config.fieldConfiguration}', font='Verdana 16 bold')],
                      [field, Column(main_column)],
                      [Button('Back', key=StudioEvents.BACK_BUTTON, font='verdana'),
                       Button('Go to Configuration Menu', key=StudioEvents.GOTO_CONFIG_BUTTON, font='verdana'),
                       Button('Exit', key=None, font='verdana')]]

            studioWindow = Window('EXPERIMENTAL GUI', layout)
            studioWindow.finalize()

            # Hide certain elements
            studioWindow[StudioEvents.START_X_TEXT].hide_row()
            studioWindow[StudioEvents.FINAL_X_TEXT].hide_row()
            studioWindow[StudioEvents.VELOCITY_INPUT].hide_row()
            studioWindow[StudioEvents.DESELECT_BUTTON].hide_row()
            studioWindow[StudioEvents.ANGLE_TEXT].hide_row()

            for z in range(1, 31):
                field.draw_line([24 * z, 720], [24 * z, 0], 'light grey')
                field.draw_line([0, 24 * z], [720, 24 * z], 'light grey')
            for x in range(1, 6):
                field.draw_line([120 * x, 720], [120 * x, 0], 'black')
                field.draw_line([0, 120 * x], [720, 120 * x], 'black')

            if config.fieldConfiguration == 'FTC Skystone':
                field.draw_line([0, 120], [120, 120], width=6, color='red')
                field.draw_line([120, 0], [120, 120], width=6, color='red')

                field.draw_line([0, 600], [120, 720], width=6, color='blue')

                field.draw_line([600, 720], [720, 600], width=6, color='red')

                field.draw_line([0, 360], [240, 360], width=6, color='blue')

                field.draw_line([480, 360], [720, 360], width=6, color='red')

                field.draw_line([240, 365], [480, 365], width=6, color='yellow')
                field.draw_line([0, 360], [240, 360], width=6, color='blue')

                field.draw_line([600, 120], [720, 120], width=6, color='blue')
                field.draw_line([600, 0], [600, 120], width=6, color='blue')

                field.draw_rectangle([240, 320], [480, 400], fill_color='#28292B')

                field.draw_line([240, 365], [480, 365], width=3, color='yellow')
                field.draw_line([240, 355], [480, 355], width=3, color='yellow')

                field.draw_rectangle([240, 690], [332.5, 517.5], fill_color='blue')
                field.draw_rectangle([387.5, 690], [480, 517.5], fill_color='red')

                field.draw_rectangle([241, 240], [261, 0], fill_color='yellow', line_width=0)
                for y in range(0, 7):
                    field.draw_line([241, y * 40], [261, y * 40], width=0.5)

            while True and config.studioActive:  # Event Loop
                config.studioEvent, config.studioValues = studioWindow.read()

                logger.debug(f'Studio Event received: {config.studioEvent}')

                if config.studioEvent is None or config.studioEvent == StudioEvents.EXIT_BUTTON:
                    config.studioActive = False
                    titleWindow.UnHide()
                    studioWindow.Close()
                    break

if __name__ == "__main__":
    main()
