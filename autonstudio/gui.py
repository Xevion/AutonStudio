"""
This file controls all GUI operations, and acts as the heart of the program with a crude PySimpleGUI interface.
"""

import logging
import math
import time

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window, Combo, Graph, InputText, Tab, TabGroup, theme, \
    Popup, PopupGetText, PopupGetFolder, PopupYesNo, PopupGetFile, PopupAnnoying

from autonstudio import manage
from autonstudio.enums import TitleEvents, ConfigEvents, StudioEvents, StudioActions
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
        # Allows handling for the Go to Configuration button in Studio
        if not config.hiddenStudio:
            config.titleEvent, config.titleValues = titleWindow.read()
        else:
            logger.debug('Hidden Studio detected. Event loop postponed.')
            config.hiddenStudio = False
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
                [Text('\n' * 8),
                 Button('Update', key=ConfigEvents.UPDATE_CONFIG, bind_return_key=True, font='verdana')]]

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
                    x, y = config.configValues[ConfigEvents.ROBOT_SIZE_X], config.configValues[
                        ConfigEvents.ROBOT_SIZE_Y]
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
                       Button('Exit', key=StudioEvents.EXIT_BUTTON, font='verdana')]]

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

                # Instantaneous Exit from AutonStudio
                if config.studioEvent == StudioEvents.EXIT_BUTTON:
                    logger.debug('Hard Exiting Studio Window')
                    config.studioActive = False
                    titleWindow.UnHide()
                    studioWindow.Close()
                    titleWindow.Close()
                    break

                # Back Button to Title Window
                if config.studioEvent is None or config.studioEvent == StudioEvents.BACK_BUTTON:
                    logger.debug('Soft Exiting Studio Window')
                    config.studioActive = False
                    titleWindow.UnHide()
                    studioWindow.Close()
                    break

                # Go to Configuration Window temporarily
                if config.studioEvent == StudioEvents.GOTO_CONFIG_BUTTON:
                    logger.debug('Exiting Studio, opening Config Window')
                    config.studioActive = False
                    config.configActive = False
                    config.hiddenStudio = True
                    studioWindow.Hide()
                    titleWindow.UnHide()
                    config.titleEvent = TitleEvents.CONFIG_BUTTON  # Set next event to be the Config Button
                    break

                # Clears all field elements and paths
                if config.studioEvent == StudioEvents.CLEAR_FIELD_BUTTON and len(config.points) > 0:
                    # Clear all points, stop rendering etc.
                    while len(config.ppoints) > 0:
                        config.ppoints.pop(0).delete()

                    # TODO: Stop rendering the robot
                    # TODO: Clear the Paths/Points tab
                    # TODO: Clear the Turns tab

                # Choose which path to edit
                if config.studioEvent == StudioEvents.EDIT_PATH_BUTTON:
                    config.pointMenuIndex = manage.Helper.getPointIndex(config.studioValues[StudioEvents.PATH_LIST][0])
                    logger.debug(f'Point Menu Index Identified: {config.pointMenuIndex}')

                # if config.studioEvent == StudioEvents.EDIT_PATH_BUTTON:
                #     counter = 0
                #     config.pathEditUpdated = False
                #     for p in config.pathStrings:
                #         counter += 1
                #         if len(config.studioValues[StudioEvents.PATH_LIST]) > 0 and config.studioValues[StudioEvents.PATH_LIST][0] == p:
                #             print(config.studioValues)
                #             studioWindow[StudioEvents.PATH_INFO].update('Path #' + str(counter))
                #             config.selectedPathNum = counter

                # Show the entry fields for editing the path
                if config.pointMenuIndex is not None and len(config.ppoints) >= 2:
                    logger.debug('Updating Point Editing Menu')
                    # Unhide input boxes
                    studioWindow[StudioEvents.START_X_TEXT].unhide_row()
                    studioWindow[StudioEvents.FINAL_X_INPUT].unhide_row()
                    studioWindow[StudioEvents.VELOCITY_INPUT].unhide_row()
                    studioWindow[StudioEvents.DESELECT_BUTTON].unhide_row()
                    # Update all of the input boxes
                    studioWindow[StudioEvents.START_X_INPUT].update(value=config.ppoints[config.pointMenuIndex].x)
                    studioWindow[StudioEvents.START_Y_INPUT].update(value=config.ppoints[config.pointMenuIndex].y)
                    studioWindow[StudioEvents.FINAL_X_INPUT].update(value=config.ppoints[config.pointMenuIndex + 1].x)
                    studioWindow[StudioEvents.FINAL_Y_INPUT].update(value=config.ppoints[config.pointMenuIndex + 1].y)
                    studioWindow[StudioEvents.VELOCITY_INPUT].update(value=config.velocities[config.pointMenuIndex])
                    config.pathEditUpdated = True

                # Change the values of a point based on what was entered into the entry field
                if config.pathEditUpdated and config.studioEvent == StudioEvents.START_X_INPUT:
                    value = manage.Helper.getDigits(config.studioValues[StudioEvents.START_X_INPUT])
                    config.ppoints[config.pointMenuIndex].x = float(value) *5 + (720 / 2)
                elif config.studioEvent == StudioEvents.START_Y_INPUT:
                    value = manage.Helper.getDigits(config.studioValues[StudioEvents.START_Y_INPUT])
                    config.points[config.pointMenuIndex].y = float(value) * 5 + (720 / 2)
                elif config.studioEvent == StudioEvents.FINAL_X_INPUT:
                    value = manage.Helper.getDigits(config.studioValues[StudioEvents.FINAL_X_INPUT])[0]
                    config.points[config.pointMenuIndex + 1].x = float(value) * 5 + (720 / 2)
                elif config.studioEvent == StudioEvents.FINAL_Y_INPUT:
                    value = manage.Helper.getDigits(config.studioValues[StudioEvents.FINAL_Y_INPUT])[0]
                    config.points[config.pointMenuIndex + 1].y = float(value) * 5 + (720 / 2)
                elif config.studioEvent == StudioEvents.VELOCITY_INPUT:
                    value = manage.Helper.getDigits(config.studioValues[StudioEvents.VELOCITY_INPUT])[0]
                    config.velocities[config.pointMenuIndex].velocity = float(value)

                # Rounds all the points to the nearest inch
                if config.studioEvent == StudioEvents.ROUND_ALL_BUTTON:
                    logger.debug('Rounding all {len(config.ppoints)} points.')
                    for p in config.ppoints:
                        p.x, p.y = round(p.x, 2), round(p.y, 2)

                # Deselect the current path
                if config.studioEvent == StudioEvents.DESELECT_BUTTON and config.pointMenuIndex is not None:
                    logger.debug('Deselecting Path Item.')
                    config.pointMenuIndex = None

                if config.selectedPathNum is None:
                    studioWindow[StudioEvents.PATH_INFO].update('None')
                    studioWindow[StudioEvents.START_X_TEXT].hide_row()
                    studioWindow[StudioEvents.FINAL_X_INPUT].hide_row()
                    studioWindow[StudioEvents.DESELECT_BUTTON].hide_row()
                    studioWindow[StudioEvents.VELOCITY_INPUT].hide_row()

                # Choose which turn to edit
                if config.studioEvent == StudioEvents.EDIT_TURN_BUTTON:
                    if config.studioValues[StudioEvents.TURN_LIST]:
                        if len(list(filter(lambda point: point.turn is not None, config.ppoints))) > 0:
                            config.turnEditorIndex = manage.Helper.getTurnIndex(
                                config.studioValues[StudioEvents.TURN_LIST][0])
                            studioWindow[StudioEvents.TURN_INFO].update(f'Turn #{config.turnEditorIndex}')
                            config.turnEditUpdated = False
                        else:
                            logger.warning('No Turns are available to be selected.')
                    else:
                        logger.warning('No Turn is Selected.')


                # if config.selectedTurnNum is None:
                #     studioWindow[StudioEvents.ANGLE_TEXT].hide_row()
                #     studioWindow[StudioEvents.TURN_INFO].update('None')
                # Show the entry fields for editing the turn
                # if config.selectedTurnNum is not None and not config.turnEditUpdated:
                #     studioWindow[StudioEvents.ANGLE_TEXT].unhide_row()
                #     studioWindow[StudioEvents.ANGLE_INPUT].update(value=config.turns[config.selectedTurnNum - 1][1])
                #     config.turnEditUpdated = True
                # Change the angle value of a turn based on what was entered into the entry field
                # if config.turnEditUpdated:
                #     if config.studioEvent == StudioEvents.ANGLE_INPUT:
                #         config.turns[config.selectedTurnNum - 1][1] = float(
                #             manage.Helper.clean_coordinates(config.studioValues[StudioEvents.ANGLE_INPUT]))

                # Select start point and draw the circle for it and add it to points
                # if config.studioEvent == StudioEvents.START_POINT_BUTTON:
                #     config.selectedOperation = StudioActions.ADD_START_POINT

                # selectStartPoint op handling
                # if config.selectedOperation == StudioActions.ADD_START_POINT:
                #     # If the user clicked on the field
                #     if config.studioEvent == StudioEvents.FIELD:
                #         field.delete_figure(config.startPoint_circle)
                #         config.startPoint_circle = field.draw_circle(
                #             [config.studioValues[StudioEvents.FIELD][0], config.studioValues[StudioEvents.FIELD][1]], 5)
                #         # handling for when start point is not already picked
                #         if len(config.points) == 0:
                #             config.points.append(None)
                #         config.points[0] = [config.studioValues[StudioEvents.FIELD][0],
                #                                   config.studioValues[StudioEvents.FIELD][1]]
                #         config.startHeading = float(manage.Helper.clean_coordinates(PopupGetText(
                #             message='Enter start heading, 0 is straight up, 90 is to the right, -90 is to the left',
                #             title='Heading selection')))
                #         config.selectedOperation = None

                # Select next point and and it to list of points
                if config.studioEvent == StudioEvents.ADD_POINT_BUTTON and len(config.points) > 0:
                    config.selectedOperation = StudioActions.ADD_POINT

                # if config.selectedOperation == StudioActions.ADD_POINT:
                #     # Add a point where the user clicked on the end of the path
                #     if config.studioEvent == StudioEvents.FIELD:
                #         config.points.append(
                #             [config.studioValues[StudioEvents.FIELD][0], config.studioValues[StudioEvents.FIELD][1]])
                #         config.velocities.append(config.defaultVelocity)
                #         config.selectedOperation = None

                # Delete Point button handling
                if config.studioEvent == StudioEvents.DELETE_POINT_BUTTON and len(config.points) > 0:
                    config.selectedOperation = StudioActions.DELETE_POINT

                # Point Deletion Handling
                # if config.selectedOperation == StudioActions.DELETE_POINT:
                #     config.selectedTurnNum = None
                #     config.selectedPathNum = None

                    # Draw the Deletion Circles
                    # if len(config.delete_point_circles) == 0:
                    #     for p in config.points[1:]:
                    #         config.delete_point_circles.append(field.draw_circle(p, 10, fill_color='red'))

                    # Check if User clicked any
                    # if config.studioEvent == StudioEvents.FIELD:
                    #     for p in config.points[1:]:  # User cannot click the first
                    #         if abs(config.studioValues[StudioEvents.FIELD][0] - p[0]) < 10 and abs(
                    #                 config.studioValues[StudioEvents.FIELD][1] - p[1]) < 10:
                    #             index = config.points.index(p)
                    #             config.points.remove(p)
                    #             turn_to_remove = None
                    #             for t in config.turns:
                    #                 if index == t[0]:
                    #                     turn_to_remove = t
                    #                 if index < t[0]:
                    #                     t[0] = t[0] - 1
                    #             if turn_to_remove is not None:
                    #                 config.turns.remove(turn_to_remove)
                    #             config.selectedOperation = None

                # Delete DelPoint markers if current action is not point deletion
                # if not config.selectedOperation == StudioActions.DELETE_POINT:
                #     if len(config.delete_point_circles) > 0:
                #         for turnCircle in config.delete_point_circles:
                #             field.delete_figure(turnCircle)
                #         config.delete_point_circles.clear()

                # Delete Turn button handling
                if config.studioEvent == StudioEvents.DELETE_TURN_BUTTON and len(config.turns) > 0:
                    config.selectedOperation = StudioActions.DELETE_TURN

                # If Turn Deletion is ready
                # if config.selectedOperation == StudioActions.DELETE_TURN:
                #     config.selectedTurnNum = None
                #     config.selectedPathNum = None

                    # If the delete circles haven't been drawn yet, fill them in
                    # if len(config.delete_turn_circles) == 0:
                    #     for t in config.turns:
                    #         config.delete_turn_circles.append(
                    #             field.draw_circle(config.points[t[0]], 10, fill_color='red'))

                    # If you click somewhere on the field, check if it's close enough to a point to count
                    # if config.studioEvent == StudioEvents.FIELD:
                    #     for t in config.turns:
                    #         if abs(config.studioValues[StudioEvents.FIELD][0] - config.points[t[0]][0]) < 10 and abs(
                    #                 config.studioValues[StudioEvents.FIELD][1] - config.points[t[0]][1]) < 10:
                    #             config.turns.remove(t)
                    #             config.selectedOperation = None

                # Delete turn-delete-markers if the current operation is not turn deletion
                # if not config.selectedOperation == StudioActions.DELETE_TURN:
                #     print(f'Delete Turn Circles: {len(config.delete_turn_circles)})')
                #     if len(config.delete_turn_circles) > 0:
                #         for turnCircle in config.delete_turn_circles:
                #             field.delete_figure(turnCircle)
                #         config.delete_turn_circles.clear()

                # Select a spot to add a turn and add it to list of turns
                if config.studioEvent == StudioEvents.ADD_TURN_BUTTON:
                    config.selectedOperation = StudioActions.ADD_TURN

                # If current action is addingTurn
                # if config.selectedOperation == StudioActions.ADD_TURN:
                #     # Turn Circle Drawing
                #     if len(config.turn_circles) == 0:
                #         for i in range(0, len(config.points)):
                #             # Only draw turn circles for points with no known turn
                #             if not any(turn[0] == i for turn in config.turns):
                #                 config.turn_circles.append(field.draw_circle(config.points[i], 10, fill_color='black'))
                #
                #     # If you click on the field, scan if it hit one of the points
                #     if config.studioEvent == StudioEvents.FIELD:
                #         for i in range(0, len(config.points)):
                #             # Only check points that do not have a turn
                #             if not any(turn[0] == i for turn in config.turns):
                #                 # Check that the point has been 'clicked'
                #                 if abs(config.studioValues[StudioEvents.FIELD][0] - config.points[i][0]) < 10 and abs(
                #                         config.studioValues[StudioEvents.FIELD][1] - config.points[i][
                #                             1]) < 10:
                #                     angle = PopupGetText('Enter turn angle in degrees', title='Turn Angle Entry')
                #                     if angle is not None:
                #                         config.turns.append([i, manage.Helper.clean_coordinates(angle)])
                #                         config.selectedOperation = None
                #                     else:
                #                         PopupAnnoying('ERROR: Please enter a value')
                #
                # # Delete TurnCircle figures if we're not using them
                # if config.selectedOperation == StudioActions.DELETE_TURN:
                #     while len(config.turn_circles) > 0:
                #         field.delete_figure(config.turn_circles.pop(0))

                # Simulate the robot running through the path
                # if config.studioEvent == StudioEvents.SIMULATE_BUTTON:
                #     prevTurn = None
                #     robotCBr = [45, -45]  # Bottom right corner and go clockwise
                #     robotCBl = [-45, -45]
                #     robotCTl = [-45, 45]
                #     robotCTr = [45, 45]
                #     robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #     rot_deltas_final = [[[45], [-45]], [[-45], [-45]], [[-45], [45]], [[45], [45]]]
                #     if abs(config.startHeading - 0.0) > 0:
                #         rot_deltas_final = manage.Helper.calculate_rotation_per_frame(points=robotPolygonPoints, angle1=0.0,
                #                                                            angle2=config.startHeading,
                #                                                            degrees_per_second=45,
                #                                                            frames_per_second=60)
                #     for i in range(1, len(config.points)):
                #         deltas = manage.Helper.calculate_movement_per_frame(config.points[i - 1], config.points[i],
                #                                                  inches_per_second=config.velocities[i - 1],
                #                                                  frames_per_second=60,
                #                                                  pixels_per_inch=5)
                #         num_movements = math.sqrt(
                #             (config.points[i][0] - config.points[i - 1][0]) ** 2 + (
                #                     config.points[i][1] - config.points[i - 1][1]) ** 2) / math.hypot(
                #             deltas[0], deltas[1])
                #         x, y = config.points[i - 1]
                #         for t in config.turns:
                #             if t[0] == i - 1:
                #                 if prevTurn is None:
                #                     angle1 = config.startHeading
                #                 else:
                #                     angle1 = prevTurn[1]
                #                 robotCBr = [45, -45]  # Bottom right corner and go clockwise
                #                 robotCBl = [-45, -45]
                #                 robotCTl = [-45, 45]
                #                 robotCTr = [45, 45]
                #                 robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #                 rot_deltas = manage.Helper.calculate_rotation_per_frame(points=robotPolygonPoints,
                #                                                              angle1=angle1,
                #                                                              angle2=t[1], degrees_per_second=45,
                #                                                              frames_per_second=60)
                #                 if abs(float(t[1]) - float(angle1)) > 0:
                #                     rot_deltas_final = rot_deltas.copy()
                #                 prevTurn = t
                #                 for j in range(0, len(rot_deltas[0][0]) - 1):
                #                     start_time = time.time()
                #                     field.delete_figure(config.robot_polygon)
                #                     field.delete_figure(config.robot_point)
                #
                #                     # Bottom right corner and go clockwise
                #                     robotCBr = [x + rot_deltas_final[0][0][j], y + rot_deltas_final[0][1][j]]
                #                     robotCBl = [x + rot_deltas_final[1][0][j], y + rot_deltas_final[1][1][j]]
                #                     robotCTl = [x + rot_deltas_final[2][0][j], y + rot_deltas_final[2][1][j]]
                #                     robotCTr = [x + rot_deltas_final[3][0][j], y + rot_deltas_final[3][1][j]]
                #                     robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #                     config.robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black',
                #                                                        line_width='3', fill_color='')
                #                     robotLinePoints = [
                #                         [
                #                             (robotCTr[0] + robotCBr[0]) / 2.0, (robotCTr[1] + robotCBr[1]) / 2.0
                #                         ],
                #                         [
                #                             ((robotCTr[0] + robotCBr[0]) / 2.0) - 20, ((robotCTr[1] + robotCBr[1]) / 2.0) - 20
                #                         ]
                #                     ]
                #                     config.robot_point = field.draw_point(point=robotLinePoints[0], color='yellow',
                #                                                    size=15)
                #                     studioWindow.refresh()
                #                     sleepTime = max(0, 1 / 60 - (time.time() - start_time))
                #                     time.sleep(sleepTime)
                #
                #         for j in range(0, int(num_movements)):
                #             start_time = time.time()
                #             x += deltas[0]
                #             y += deltas[1]
                #             field.delete_figure(config.robot_polygon)
                #             field.delete_figure(config.robot_point)
                #             robotCBr = [x + rot_deltas_final[0][0][-1],
                #                         y + rot_deltas_final[0][1][-1]]  # Bottom right corner and go clockwise
                #             robotCBl = [x + rot_deltas_final[1][0][-1], y + rot_deltas_final[1][1][-1]]
                #             robotCTl = [x + rot_deltas_final[2][0][-1], y + rot_deltas_final[2][1][-1]]
                #             robotCTr = [x + rot_deltas_final[3][0][-1], y + rot_deltas_final[3][1][-1]]
                #             robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #             config.robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black',
                #                                                line_width='3',
                #                                                fill_color='')
                #             config.robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                #             if config.startHeading == 0 and rot_deltas_final == [[[45], [-45]], [[-45], [-45]],
                #                                                           [[-45], [45]],
                #                                                           [[45], [45]]]:
                #                 config.robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0),
                #                               ((robotCTr[1] + robotCTl[1]) / 2.0)]
                #             config.robot_point = field.draw_point(point=config.robotPoint, color='yellow', size=15)
                #             studioWindow.refresh()
                #             sleepTime = 1 / 60 - (time.time() - start_time)
                #             if sleepTime < 0:
                #                 sleepTime = 0
                #             time.sleep(sleepTime)
                #     config.selectedOperation = None

                # if config.studioEvent == StudioEvents.EXPORT_BUTTON:
                #     if len(config.convertedPoints) > 0:
                #         export_location = ''
                #         while export_location == '':
                #             export_location = PopupGetFolder('Choose Export Location')
                #         if export_location is not None:
                #             export_location = export_location + '/AutonPath.java'
                #             export_file = open(export_location, 'w')
                #             export_string = ''
                #             export_string += 'package org.firstinspires.ftc.teamcode;\n\n'
                #             export_string += 'import com.qualcomm.robotcore.eventloop.opmode.Autonomous;\n\n'
                #             export_string += '@Autonomous\n'
                #             export_string += 'public class AutonPath extends PositionBasedAuton3 {\n'
                #             export_string += 'public void setStartPos(){\n'
                #             export_string += f'startX = {config.convertedPoints[0][0]}; startY = {config.convertedPoints[0][1]};\n'
                #             export_string += f'startOrientation = {config.startHeading};\n'
                #             export_string += '}\n\n'
                #             export_string += 'public void drive(){\n'
                #             heading = config.startHeading
                #             for i in range(1, len(config.points)):
                #                 for t in config.turns:
                #                     if t[0] == i - 1:
                #                         export_string += f'turn({t[1]},TURN_SPEED,positioning);\n'
                #                         heading = t[1]
                #                 export_string += f'driveToPosition({config.convertedPoints[i][0]},{config.convertedPoints[i][1]},DRIVE_SPEED,{heading},0,0,positioning,sensing);\n'
                #             export_string += '}}'
                #             export_file.write(export_string)
                #             Popup('Export Successful!')
                #     else:
                #         Popup('No Paths to Export')
                #
                # if config.studioEvent == StudioEvents.SAVE_BUTTON:
                #     save_name = ''
                #     while save_name == '':
                #         save_name = PopupGetText('Name:')
                #     if save_name is not None:
                #         save_location = PopupGetFolder('', no_window=True)
                #         save_location = save_location + '/' + save_name + '.auton'
                #         save_file = open(save_location, 'w')
                #         save_string = ''
                #         save_string += str(len(config.points)) + '\n'
                #         for p in config.points:
                #             save_string += f'{p[0]} {p[1]}\n'
                #         save_string += str(len(config.turns)) + '\n'
                #         for t in config.turns:
                #             save_string += f'{t[0]} {t[1]}\n'
                #         save_file.write(save_string)
                #         save_file.close()

                # if config.studioEvent == StudioEvents.LOAD_BUTTON:
                #     choice = PopupYesNo(
                #         'Do you want to load a save?\nYou will lose any unsaved progress if you do so.')
                #     if choice == 'Yes':
                #         config.points.clear()
                #         config.turns.clear()
                #         config.velocities.clear()
                #         save_location = PopupGetFile('Hello', no_window=True,
                #                                      file_types=(("Auton Files", "*.auton"),))
                #         save_file = open(save_location, 'r')
                #         num_points = int(save_file.readline())
                #         for i in range(num_points):
                #             line = save_file.readline().split()
                #             config.points.append([int(line[0]), int(line[1])])
                #             config.velocities.append(config.defaultVelocity)
                #         num_turns = int(save_file.readline())
                #         for i in range(num_turns):
                #             line = save_file.readline().split()
                #             config.turns.append([int(line[0]), int(line[1])])
                #         save_file.close()

                # Add points and turns to list of paths and turns, then display them in the path and turn list
                # config.pathStrings = []
                # config.convertedPoints = manage.Helper.convert_coordinates_to_inches(config.points, pixels_per_inch=5,
                #                                                               field_length_inches=144)
                # heading = config.startHeading
                # prevTurn = None
                # for i in range(1, len(config.points)):
                #     for t in config.turns:
                #         if t[0] == i - 1:
                #             if prevTurn is None:
                #                 heading = config.startHeading
                #             else:
                #                 heading = prevTurn[1]
                #         prevTurn = t
                #     config.pathStrings.append(
                #         'Path #' + str(i) + ': ' + manage.Helper.generate_path_string(config.convertedPoints[i - 1],
                #                                                                       config.convertedPoints[i],
                #                                                                       config.velocities[i - 1],
                #                                                                       heading))
                # studioWindow[StudioEvents.PATH_LIST].update(values=config.pathStrings)
                # config.turnStrings = []
                # config.turns = manage.Helper.sort_turns(config.turns)
                # for i in range(0, len(config.turns)):
                #     config.turnStrings.append(
                #         'Turn #' + str(i + 1) + ": " + manage.Helper.generate_turn_string(config.turns[i], config.convertedPoints))
                # studioWindow[StudioEvents.TURN_LIST].update(values=config.turnStrings)

                # Draw turn indicators
                # for i in range(len(config.turnIndicator_circles)):
                #     field.delete_figure(config.turnIndicator_circles[i])
                #     field.delete_figure(config.turnIndicator_text[i])
                # for i in range(0, len(config.turns)):
                #     if len(config.turnIndicator_circles) < i + 1:
                #         config.turnIndicator_circles.append(None)
                #         config.turnIndicator_text.append(None)
                #     config.turnIndicator_circles[i] = field.draw_circle(config.points[config.turns[i][0]], 5,
                #                                                         fill_color='black')
                #     config.turnIndicator_text[i] = field.draw_text(text=str(config.turns[i][1]) + '°',
                #                                                    location=[config.points[config.turns[i][0]][0] + 10,
                #                                                              config.points[config.turns[i][0]][1] + 10],
                #                                                    color='dark blue')

                # Draw robot on the field and ensures the robot cannot be magically clipping through
                # the field walls (robot starts touching field wall if outside boundary)
                # if len(config.points) > 0:
                #     field.delete_figure(config.robot_polygon)
                #     field.delete_figure(config.robot_point)
                #     robotCBr = [45, -45]  # Bottom right corner and go clockwise
                #     robotCBl = [-45, -45]
                #     robotCTl = [-45, 45]
                #     robotCTr = [45, 45]
                #     robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #     rot_deltas_final = [[[45], [-45]], [[-45], [-45]], [[-45], [45]], [[45], [45]]]
                #     if abs(config.startHeading - 0.0) > 0:
                #         rot_deltas_final = manage.Helper.calculate_rotation_per_frame(points=robotPolygonPoints, angle1=0.0,
                #                                                            angle2=config.startHeading,
                #                                                            degrees_per_second=45,
                #                                                            frames_per_second=60)
                #     robotCBr = [config.points[0][0] + rot_deltas_final[0][0][-1],
                #                 config.points[0][1] + rot_deltas_final[0][1][
                #                     -1]]  # Bottom right corner and go clockwise
                #     robotCBl = [config.points[0][0] + rot_deltas_final[1][0][-1],
                #                 config.points[0][1] + rot_deltas_final[1][1][-1]]
                #     robotCTl = [config.points[0][0] + rot_deltas_final[2][0][-1],
                #                 config.points[0][1] + rot_deltas_final[2][1][-1]]
                #     robotCTr = [config.points[0][0] + rot_deltas_final[3][0][-1],
                #                 config.points[0][1] + rot_deltas_final[3][1][-1]]
                #     robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                #     config.robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black', line_width='3',
                #                                        fill_color='')
                #     config.robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                #     if config.startHeading == 0:
                #         config.robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0), ((robotCTr[1] + robotCTl[1]) / 2.0)]
                #     config.robot_point = field.draw_point(point=config.robotPoint, color='yellow', size=15)
                #
                #     # Draw lines between all points
                #     print(config.points)
                #     if len(config.points) > 0:
                #         field.delete_figure(config.startPoint_circle)
                #         config.startPoint_circle = field.draw_circle(config.points[0], 5)
                #     field.delete_figure(config.startPoint_line)
                #     if len(config.points) > 1:
                #         lineColor = 'black'
                #         if config.selectedPathNum == 1:
                #             lineColor = 'yellow'
                #         config.startPoint_line = field.draw_line(config.points[0], config.points[1], color=lineColor,
                #                                           width=2.0)
                #     for pl in config.point_lines:
                #         field.delete_figure(pl)
                #     for i in range(2, len(config.points)):
                #         lineColor = 'black'
                #         if config.selectedPathNum == i:
                #             lineColor = 'yellow'
                #         if len(config.point_lines) < i - 1:
                #             config.point_lines.append(None)
                #         config.point_lines[i - 2] = (
                #             field.draw_line(config.points[i - 1], config.points[i], color=lineColor, width=2.0))

                # export_file.close()
                # titleWindow.close()


if __name__ == "__main__":
    main()
