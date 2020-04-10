"""
This file controls all GUI operations, and acts as the heart of the program with a crude PySimpleGUI interface.
"""

import logging
import time

from PySimpleGUI import Text, Button, Listbox, Column, Image, Window, Combo, Graph, InputText, Tab, TabGroup, theme, \
    Popup, PopupGetText, PopupGetFolder, PopupYesNo

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
                if event1 == '-CLEAR_FIELD_BUTTON-' and len(points) > 0:
                    field.delete_figure(robot_rectangle)
                    field.delete_figure(robot_polygon)
                    field.delete_figure(robot_point)
                    field.delete_figure(startPoint_circle)
                    for tc in turn_circles:
                        field.delete_figure(tc)
                    for tic in turnIndicator_circles:
                        field.delete_figure(tic)
                    field.delete_figure(startPoint_line)
                    for pl in point_lines:
                        field.delete_figure(pl)
                    for tit in turnIndicator_text:
                        field.delete_figure(tit)
                    points.clear()
                    point_lines.clear()
                    turn_circles.clear()
                    turnIndicator_circles.clear()
                    turnIndicator_text.clear()
                    turns.clear()
                    convertedPoints.clear()
                    pathStrings.clear()
                    turnStrings.clear()
                    fieldSave = None

                # Choose which path to edit
                if event1 == '-EDIT_PATH_BUTTON-':
                    counter = 0
                    pathEditUpdated = False
                    for p in pathStrings:
                        counter += 1
                        if len(values1['-PATH_LIST-']) > 0 and values1['-PATH_LIST-'][0] == p:
                            studioWindow['-PATH_INFO-'].update('Path #' + str(counter))
                            selectedPathNum = counter

                # Show the entry fields for editing the path
                if selectedPathNum is not None and not pathEditUpdated:
                    studioWindow[StudioEvents.START_X_TEXT].unhide_row()
                    studioWindow['-FINAL_X_TEXT-'].unhide_row()
                    studioWindow['-VELOCITY_INPUT-'].unhide_row()
                    studioWindow['-DESELECT_BUTTON-'].unhide_row()
                    studioWindow['-START_X_INPUT-'].update(value=convertedPoints[selectedPathNum - 1][0])
                    studioWindow['-START_Y_INPUT-'].update(value=convertedPoints[selectedPathNum - 1][1])
                    studioWindow['-FINAL_X_INPUT-'].update(value=convertedPoints[selectedPathNum][0])
                    studioWindow['-FINAL_Y_INPUT-'].update(value=convertedPoints[selectedPathNum][1])
                    studioWindow['-VELOCITY_INPUT-'].update(value=velocities[selectedPathNum - 1])
                    pathEditUpdated = True
                # Change the values of a point based on what was entered into the entry field
                if pathEditUpdated and config.studioEvent == StudioEvents.START_X_INPUT:
                    points[selectedPathNum - 1][0] = float(
                        hf.clean_coordinates(config.studioValues['-START_X_INPUT-'])) * 5 + (720 / 2)
                    elif event1 == '-START_Y_INPUT-':
                        points[selectedPathNum - 1][1] = float(
                            hf.clean_coordinates(config.studioValues['-START_Y_INPUT-'])) * 5 + (
                                                                 720 / 2)
                    elif event1 == '-FINAL_X_INPUT-':
                        points[selectedPathNum][0] = float(hf.clean_coordinates(config.studioValues['-FINAL_X_INPUT-'])) * 5 + (
                                    720 / 2)
                    elif event1 == '-FINAL_Y_INPUT-':
                        points[selectedPathNum][1] = float(hf.clean_coordinates(config.studioValues['-FINAL_Y_INPUT-'])) * 5 + (
                                    720 / 2)
                    elif event1 == '-VELOCITY_INPUT-':
                        velocities[selectedPathNum - 1] = float(hf.clean_coordinates(config.studioValues['-VELOCITY_INPUT-']))

                # Rounds all the points to the nearest inch
                if event1 == '-ROUND_ALL_BUTTON-':
                    for i in range(0, len(convertedPoints)):
                        points[i][0] = round(convertedPoints[i][0]) * 5 + (720 / 2)
                        points[i][1] = round(convertedPoints[i][1]) * 5 + (720 / 2)

                # Deselect the current path
                if event1 == '-DESELECT_BUTTON-':
                    selectedPathNum = None
                if selectedPathNum is None:
                    studioWindow['-PATH_INFO-'].update('None')
                    studioWindow['-START_X_TEXT-'].hide_row()
                    studioWindow['-FINAL_X_TEXT-'].hide_row()
                    studioWindow['-DESELECT_BUTTON-'].hide_row()
                    studioWindow['-VELOCITY_INPUT-'].hide_row()

                # Choose which turn to edit
                if event1 == '-EDIT_TURN_BUTTON-':
                    counter = 0
                    turnEditUpdated = False
                    for t in turnStrings:
                        counter += 1
                        if len(config.studioValues['-TURN_LIST-']) > 0 and config.studioValues['-TURN_LIST-'][0] == t:
                            studioWindow['-TURN_INFO-'].update('Turn #' + str(counter))
                            selectedTurnNum = counter

                if selectedTurnNum is None:
                    studioWindow['-ANGLE_TEXT-'].hide_row()
                    studioWindow['-TURN_INFO-'].update('None')
                # Show the entry fields for editing the turn
                if selectedTurnNum is not None and not turnEditUpdated:
                    studioWindow['-ANGLE_TEXT-'].unhide_row()
                    studioWindow['-ANGLE_INPUT-'].update(value=turns[selectedTurnNum - 1][1])
                    turnEditUpdated = True
                # Change the angle value of a turn based on what was entered into the entry field
                if turnEditUpdated:
                    if event1 == '-ANGLE_INPUT-':
                        turns[selectedTurnNum - 1][1] = float(hf.clean_coordinates(config.studioValues['-ANGLE_INPUT-']))

                # Select start point and draw the circle for it and add it to points
                if event1 == '-START_POINT_BUTTON-':
                    selectedOperation = 'selectingStartPoint'
                if selectedOperation == 'selectingStartPoint':
                    if event1 == '-FIELD-':
                        field.delete_figure(startPoint_circle)
                        startPoint_circle = field.draw_circle([config.studioValues['-FIELD-'][0], config.studioValues['-FIELD-'][1]], 5)
                        if len(points) > 0:
                            points[0] = ([config.studioValues['-FIELD-'][0], config.studioValues['-FIELD-'][1]])
                        else:
                            points.append([config.studioValues['-FIELD-'][0], config.studioValues['-FIELD-'][1]])
                        startHeading = float(hf.clean_coordinates(sg.PopupGetText(
                            message='Enter start heading, 0 is straight up, 90 is to the right, -90 is to the left',
                            title='Heading selection')))
                        selectedOperation = None

                # Select next point and and it to list of points
                if event1 == '-ADD_POINT_BUTTON-' and len(points) > 0:
                    selectedOperation = 'addingPoint'
                if selectedOperation == 'addingPoint':
                    if event1 == '-FIELD-':
                        points.append([config.studioValues['-FIELD-'][0], config.studioValues['-FIELD-'][1]])
                        velocities.append(defaultVelocity)
                        selectedOperation = None

                if event1 == '-DELETE_POINT_BUTTON-' and len(points) > 0:
                    selectedOperation = 'deletingPoint'
                if selectedOperation == 'deletingPoint':
                    selectedTurnNum = None
                    selectedPathNum = None
                    if len(delete_point_circles) == 0:
                        for p in points[1:]:
                            delete_point_circles.append(field.draw_circle(p, 10, fill_color='red'))
                    if event1 == '-FIELD-':
                        for p in points[1:]:
                            if abs(config.studioValues['-FIELD-'][0] - p[0]) < 10 and abs(config.studioValues['-FIELD-'][1] - p[1]) < 10:
                                indx = points.index(p)
                                points.remove(p)
                                turn_to_remove = None
                                for t in turns:
                                    if indx == t[0]:
                                        turn_to_remove = t
                                    if indx < t[0]:
                                        t[0] = t[0] - 1
                                if turn_to_remove is not None:
                                    turns.remove(turn_to_remove)
                                selectedOperation = None
                if not selectedOperation == 'deletingPoint':
                    if len(delete_point_circles) > 0:
                        for c in delete_point_circles:
                            field.delete_figure(c)
                        delete_point_circles.clear()

                if event1 == '-DELETE_TURN_BUTTON-' and len(turns) > 0:
                    selectedOperation = 'deletingTurn'
                if selectedOperation == 'deletingTurn':
                    selectedTurnNum = None
                    selectedPathNum = None
                    if len(delete_turn_circles) == 0:
                        for t in turns:
                            delete_turn_circles.append(field.draw_circle(points[t[0]], 10, fill_color='red'))
                    if event1 == '-FIELD-':
                        for t in turns:
                            if abs(values1['-FIELD-'][0] - points[t[0]][0]) < 10 and abs(
                                    values1['-FIELD-'][1] - points[t[0]][1]) < 10:
                                turns.remove(t)
                                selectedOperation = None
                if not selectedOperation == 'deletingTurn':
                    print(len(delete_turn_circles))
                    if len(delete_turn_circles) > 0:
                        for c in delete_turn_circles:
                            field.delete_figure(c)
                        delete_turn_circles.clear()

                # Select a spot to add a turn and add it to list of turns
                if event1 == '-ADD_TURN_BUTTON-':
                    selectedOperation = 'addingTurn'
                if selectedOperation == 'addingTurn':
                    if len(turn_circles) == 0:
                        for i in range(0, len(points)):
                            drawCircle = True
                            for t in turns:
                                if t[0] == i:
                                    drawCircle = False
                            if drawCircle:
                                turn_circles.append(field.draw_circle(points[i], 10, fill_color='black'))
                    if event1 == '-FIELD-':
                        for i in range(0, len(points)):
                            allowPointToBeSelected = True
                            for t in turns:
                                if t[0] == i:
                                    allowPointToBeSelected = False
                            if abs(values1['-FIELD-'][0] - points[i][0]) < 10 and abs(
                                    values1['-FIELD-'][1] - points[i][1]) < 10 and allowPointToBeSelected:
                                angle = sg.PopupGetText('Enter turn angle in degrees', title='Turn Angle Entry')
                                if angle is not None:
                                    turns.append([i, hf.clean_coordinates(angle)])
                                    selectedOperation = None
                                else:
                                    sg.PopupAnnoying('ERROR: Please enter a value')
                if not selectedOperation == 'addingTurn':
                    if len(turn_circles) > 0:
                        for c in turn_circles:
                            field.delete_figure(c)
                        turn_circles.clear()

                # Simulate the robot running through the path
                if event1 == '-SIMULATE_BUTTON-':
                    selectedOperation = 'simulating'
                if selectedOperation == 'simulating':
                    prevTurn = None
                    robotCBr = [45, -45]  # Bottom right corner and go clockwise
                    robotCBl = [-45, -45]
                    robotCTl = [-45, 45]
                    robotCTr = [45, 45]
                    robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                    rot_deltas_final = [[[45], [-45]], [[-45], [-45]], [[-45], [45]], [[45], [45]]]
                    if abs(startHeading - 0.0) > 0:
                        rot_deltas_final = hf.calculate_rotation_per_frame(points=robotPolygonPoints, angle1=0.0,
                                                                           angle2=startHeading,
                                                                           degrees_per_second=45,
                                                                           frames_per_second=60)
                    for i in range(1, len(points)):
                        deltas = hf.calculate_movement_per_frame(points[i - 1], points[i],
                                                                 inches_per_second=velocities[i - 1],
                                                                 frames_per_second=60,
                                                                 pixels_per_inch=5)
                        num_movements = math.sqrt(
                            (points[i][0] - points[i - 1][0]) ** 2 + (
                                        points[i][1] - points[i - 1][1]) ** 2) / math.hypot(
                            deltas[0], deltas[1])
                        x, y = points[i - 1]
                        for t in turns:
                            if t[0] == i - 1:
                                if prevTurn is None:
                                    angle1 = startHeading
                                else:
                                    angle1 = prevTurn[1]
                                robotCBr = [45, -45]  # Bottom right corner and go clockwise
                                robotCBl = [-45, -45]
                                robotCTl = [-45, 45]
                                robotCTr = [45, 45]
                                robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                                rot_deltas = hf.calculate_rotation_per_frame(points=robotPolygonPoints,
                                                                             angle1=angle1,
                                                                             angle2=t[1], degrees_per_second=45,
                                                                             frames_per_second=60)
                                if abs(float(t[1]) - float(angle1)) > 0:
                                    rot_deltas_final = rot_deltas.copy()
                                prevTurn = t
                                for j in range(0, len(rot_deltas[0][0]) - 1):
                                    start_time = time.time()
                                    field.delete_figure(robot_polygon)
                                    field.delete_figure(robot_point)
                                    robotCBr = [x + rot_deltas_final[0][0][j],
                                                y + rot_deltas_final[0][1][
                                                    j]]  # Bottom right corner and go clockwise
                                    robotCBl = [x + rot_deltas_final[1][0][j], y + rot_deltas_final[1][1][j]]
                                    robotCTl = [x + rot_deltas_final[2][0][j], y + rot_deltas_final[2][1][j]]
                                    robotCTr = [x + rot_deltas_final[3][0][j], y + rot_deltas_final[3][1][j]]
                                    robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                                    robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black',
                                                                       line_width='3', fill_color='')
                                    robotLinePoints = [
                                        [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)],
                                        [((robotCTr[0] + robotCBr[0]) / 2.0) - 20,
                                         ((robotCTr[1] + robotCBr[1]) / 2.0) - 20]]
                                    robot_point = field.draw_point(point=robotLinePoints[0], color='yellow',
                                                                   size=15)
                                    studioWindow.refresh()
                                    sleepTime = max(0, 1 / 60 - (time.time() - start_time)
                                    time.sleep(sleepTime)
                        for j in range(0, int(num_movements)):
                            start_time = time.time()
                            x += deltas[0]
                            y += deltas[1]
                            field.delete_figure(robot_polygon)
                            field.delete_figure(robot_point)
                            robotCBr = [x + rot_deltas_final[0][0][-1],
                                        y + rot_deltas_final[0][1][-1]]  # Bottom right corner and go clockwise
                            robotCBl = [x + rot_deltas_final[1][0][-1], y + rot_deltas_final[1][1][-1]]
                            robotCTl = [x + rot_deltas_final[2][0][-1], y + rot_deltas_final[2][1][-1]]
                            robotCTr = [x + rot_deltas_final[3][0][-1], y + rot_deltas_final[3][1][-1]]
                            robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                            robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black',
                                                               line_width='3',
                                                               fill_color='')
                            robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                            if startHeading == 0 and rot_deltas_final == [[[45], [-45]], [[-45], [-45]],
                                                                          [[-45], [45]],
                                                                          [[45], [45]]]:
                                robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0),
                                              ((robotCTr[1] + robotCTl[1]) / 2.0)]
                            robot_point = field.draw_point(point=robotPoint, color='yellow', size=15)
                            studio_window.refresh()
                            sleepTime = 1 / 60 - (time.time() - start_time)
                            if sleepTime < 0:
                                sleepTime = 0
                            time.sleep(sleepTime)
                    selectedOperation = None

                if config.studioEvent == StudioEvents.EXPORT_BUTTON:
                    if len(convertedPoints) > 0:
                        export_location = ''
                        while export_location == '':
                            export_location = sg.PopupGetFolder('Choose Export Location')
                        if export_location is not None:
                            export_location = export_location + '/AutonPath.java'
                            export_file = open(export_location, 'w')
                            export_string = ''
                            export_string += 'package org.firstinspires.ftc.teamcode;\n\n'
                            export_string += 'import com.qualcomm.robotcore.eventloop.opmode.Autonomous;\n\n'
                            export_string += '@Autonomous\n'
                            export_string += 'public class AutonPath extends PositionBasedAuton3 {\n'
                            export_string += 'public void setStartPos(){\n'
                            export_string += f'startX = {convertedPoints[0][0]}; startY = {convertedPoints[0][1]};\n'
                            export_string += f'startOrientation = {startHeading};\n'
                            export_string += '}\n\n'
                            export_string += 'public void drive(){\n'
                            heading = startHeading
                            for i in range(1, len(points)):
                                for t in turns:
                                    if t[0] == i - 1:
                                        export_string += f'turn({t[1]},TURN_SPEED,positioning);\n'
                                        heading = t[1]
                                export_string += f'driveToPosition({convertedPoints[i][0]},{convertedPoints[i][1]},DRIVE_SPEED,{heading},0,0,positioning,sensing);\n'
                            export_string += '}}'
                            export_file.write(export_string)
                            Popup('Export Successful!')
                    else:
                        Popup('No Paths to Export')

                if config.studioEvent == StudioEvents.SAVE_BUTTON:
                    save_name = ''
                    while save_name == '':
                        save_name = PopupGetText('Name:')
                    if save_name is not None:
                        save_location = PopupGetFolder('', no_window=True)
                        save_location = save_location + '/' + save_name + '.auton'
                        save_file = open(save_location, 'w')
                        save_string = ''
                        save_string += str(len(points)) + '\n'
                        for p in points:
                            save_string += f'{p[0]} {p[1]}\n'
                        save_string += str(len(turns)) + '\n'
                        for t in turns:
                            save_string += f'{t[0]} {t[1]}\n'
                        save_file.write(save_string)
                        save_file.close()

                if event1 == '-LOAD_BUTTON-':
                    choice = PopupYesNo(
                        'Do you want to load a save?\nYou will lose any unsaved progress if you do so.')
                    if choice == 'Yes':
                        points.clear()
                        turns.clear()
                        velocities.clear()
                        save_location = sg.PopupGetFile('Hello', no_window=True,
                                                        file_types=(("Auton Files", "*.auton"),))
                        save_file = open(save_location, 'r')
                        num_points = int(save_file.readline())
                        for i in range(num_points):
                            line = save_file.readline().split()
                            config.points.append([int(line[0]), int(line[1])])
                            config.velocities.append(config.defaultVelocity)
                        num_turns = int(save_file.readline())
                        for i in range(num_turns):
                            line = save_file.readline().split()
                            turns.append([int(line[0]), int(line[1])])
                        save_file.close()

                # Add points and turns to list of paths and turns, then display them in the path and turn list
                pathStrings = []
                convertedPoints = hf.convert_coordinates_to_inches(config.points, pixels_per_inch=5,
                                                                   field_length_inches=144)
                heading = startHeading
                prevTurn = None
                for i in range(1, len(config.points)):
                    for t in turns:
                        if t[0] == i - 1:
                            if prevTurn is None:
                                heading = startHeading
                            else:
                                heading = prevTurn[1]
                        prevTurn = t
                    pathStrings.append(
                        'Path #' + str(i) + ': ' + hf.generate_path_string(convertedPoints[i - 1],
                                                                           convertedPoints[i],
                                                                           config.velocities[i - 1], heading))
                studioWindow[StudioEvents.PATH_LIST].update(values=pathStrings)
                turnStrings = []
                turns = hf.sort_turns(turns)
                for i in range(0, len(turns)):
                    turnStrings.append(
                        'Turn #' + str(i + 1) + ": " + hf.generate_turn_string(turns[i], convertedPoints))
                studioWindow[StudioEvents.TURN_LIST].update(values=turnStrings)

                # Draw turn indicators
                for i in range(len(turnIndicator_circles)):
                    field.delete_figure(turnIndicator_circles[i])
                    field.delete_figure(turnIndicator_text[i])
                for i in range(0, len(turns)):
                    if len(turnIndicator_circles) < i + 1:
                        turnIndicator_circles.append(None)
                        turnIndicator_text.append(None)
                    turnIndicator_circles[i] = field.draw_circle(config.points[turns[i][0]], 5, fill_color='black')
                    turnIndicator_text[i] = field.draw_text(text=str(turns[i][1]) + '°',
                                                            location=[config.points[turns[i][0]][0] + 10,
                                                                      config.points[turns[i][0]][1] + 10],
                                                            color='dark blue')

                # Draw robot on the field and ensures the robot cannot be magically clipping through
                # the field walls (robot starts touching field wall if outside boundary)
                if len(config.points) > 0:
                    field.delete_figure(robot_polygon)
                    field.delete_figure(robot_point)
                    robotCBr = [45, -45]  # Bottom right corner and go clockwise
                    robotCBl = [-45, -45]
                    robotCTl = [-45, 45]
                    robotCTr = [45, 45]
                    robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                    rot_deltas_final = [[[45], [-45]], [[-45], [-45]], [[-45], [45]], [[45], [45]]]
                    if abs(startHeading - 0.0) > 0:
                        rot_deltas_final = hf.calculate_rotation_per_frame(points=robotPolygonPoints, angle1=0.0,
                                                                           angle2=startHeading,
                                                                           degrees_per_second=45,
                                                                           frames_per_second=60)
                    robotCBr = [config.points[0][0] + rot_deltas_final[0][0][-1],
                                config.points[0][1] + rot_deltas_final[0][1][-1]]  # Bottom right corner and go clockwise
                    robotCBl = [config.points[0][0] + rot_deltas_final[1][0][-1],
                                config.points[0][1] + rot_deltas_final[1][1][-1]]
                    robotCTl = [config.points[0][0] + rot_deltas_final[2][0][-1],
                                config.points[0][1] + rot_deltas_final[2][1][-1]]
                    robotCTr = [config.points[0][0] + rot_deltas_final[3][0][-1],
                                config.points[0][1] + rot_deltas_final[3][1][-1]]
                    robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                    robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black', line_width='3',
                                                       fill_color='')
                    robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                    if startHeading == 0:
                        robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0), ((robotCTr[1] + robotCTl[1]) / 2.0)]
                    robot_point = field.draw_point(point=robotPoint, color='yellow', size=15)

                    # Draw lines between all points
                    print(config.points)
                    if len(config.points) > 0:
                        field.delete_figure(startPoint_circle)
                        startPoint_circle = field.draw_circle(config.points[0], 5)
                    field.delete_figure(startPoint_line)
                    if len(config.points) > 1:
                        lineColor = 'black'
                        if selectedPathNum == 1:
                            lineColor = 'yellow'
                        startPoint_line = field.draw_line(config.points[0], config.points[1], color=lineColor, width=2.0)
                    for pl in config.point_lines:
                        field.delete_figure(pl)
                    for i in range(2, len(config.points)):
                        lineColor = 'black'
                        if selectedPathNum == i:
                            lineColor = 'yellow'
                        if len(config.point_lines) < i - 1:
                            config.point_lines.append(None)
                        config.point_lines[i - 2] = (field.draw_line(config.points[i - 1], config.points[i], color=lineColor, width=2.0))

                export_file.close()
                titleWindow.close()

if __name__ == "__main__":
    main()
