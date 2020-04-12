import math
import time

import PySimpleGUI as sg

import HelperFunctions as hf

if __name__ == '__main__':

    fieldSave_MASTER = None

    sg.theme('Dark Green')  # please make your windows colorful
    logo = sg.Image('resources/autonStudioLogo.png')

    drive_selection = [sg.Listbox(['Mechanum with Odometry', 'Mechanum without Odometry', 'H-Drive with Odometry',
                                   'H-Drive without Odometry'], enable_events=True, key='-DRIVETRAIN_SELECTION-',
                                  size=(25, 4), default_values='Mechanum with Odometry', font='verdana')]

    menu_column = [[sg.Text('\n\n')],
                   [sg.Button('Click to Continue to Studio', key='-CONTINUE_BUTTON-', font='verdana')],
                   [sg.Button('Add Configuration', key='-CONFIG_BUTTON-', font='Verdana')],
                   drive_selection]

    layout2 = [[sg.Text('Welcome to Auton Studio', text_color='Black', font='Verdana 20 bold', justification='center',
                        size=[32, 1])], [logo, sg.Column(menu_column)]]

    title_window = sg.Window('Auton Studio', layout2)

    # f = open("testFile.txt", "x") This can be used to create a file. Very easy. Nice.

    # Fields used during the loop
    drivetrain = '[Mechanum with Odometry]'
    robotSize_X = None
    robotSize_Y = None
    fieldConfiguration = 'None'
    configRobot_rectangle = None
    selectedOperation = None
    pathEditUpdated = False
    turnEditUpdated = False
    startPoint_circle = None
    startPoint_line = None
    robot_rectangle = None
    robot_point = None
    robot_polygon = None
    point_lines = []
    turn_circles = []
    delete_point_circles = []
    delete_turn_circles = []
    turnIndicator_circles = []
    turnIndicator_text = []
    points = []
    turns = []
    velocities = []
    defaultVelocity = 48
    convertedPoints = []
    pathStrings = [None]
    turnStrings = [None]
    selectedPathNum = None
    selectedTurnNum = None
    startHeading = 0.0
    export_file = open('AutonPath.java', 'w')
    fieldSaves = []
    fieldSaves_NAMES = []
    saves = {}



    studioWindowActive = False
    configWindowActive = False
    changingWindow = False

    while True:
        if not changingWindow:
            event0, values0 = title_window.read()

        changingWindow = False


        print(str(event0))

        if event0 is None or event0 == 'Exit:':
            break

        if event0 == '-DRIVETRAIN_SELECTION-':
            drivetrain = values0

        if not configWindowActive and event0 == '-CONFIG_BUTTON-':
            configWindowActive = True



            configLayout = [[sg.Button('Test Button')]]
            canvas = sg.Graph(canvas_size=[300, 300], graph_bottom_left=[0, 0], graph_top_right=[350, 350],
                              background_color=None, key='-CANVAS-', enable_events=True)

            options_tab0 = [[sg.Text('\n\n\n')], [sg.Button('Add Servo', key='-ADD_SERVO_BUTTON-', font='verdana')],
                            [sg.Button('Add Hex Core Motor', key='-ADD_HEX_CORE_BUTTON-', font='verdana')],
                            [sg.Text('Select Field Configuration', font='verdana')],
                            [sg.Combo(['FTC Skystone', 'FTC Rover Ruckus', 'None'], enable_events=True, key='-FIELD_DD-'
                                      , default_value=fieldConfiguration, font='verdana')],
                            [sg.Text('\nInput Robot Size in Inches (X by Y)', font='verdana')],
                            [sg.InputText(enable_events=True, size=[4, 1], key='-ROBOT_SIZE_X-', font='verdana'), sg.Text('by', font='verdana'),
                             sg.InputText(enable_events=True, size=[4, 1], key='-ROBOT_SIZE_Y-', font='verdana')],
                            [sg.Text('\n\n\n\n\n\n\n\n'), sg.Button('Update', key='-UPDATE_CONFIG-', bind_return_key=True, font='verdana')]]




            configLayout = [[canvas, sg.Column(options_tab0)], [sg.Button("Back", key='-CONFIG_BACK_BUTTON-', font='verdana'), sg.Button('Go to Studio', key='-GOTO_STUDIO_BUTTON-', font='verdana')]]

            configWindow = sg.Window('Configuration Menu', configLayout)
            configWindow.finalize()



            canvas.draw_rectangle([2, 2], [348, 348], line_color='black', line_width=5)
            canvas.draw_line([13, 20], [337, 20], color='black', width=2)  # 18 pixels is one inch
            canvas.draw_text('18 in.', [162, 13], color='black' , font='Verdana 7 bold')

            while True and configWindowActive:
                eventC, valuesC = configWindow.Read()

                if eventC is None or eventC == '-CONFIG_BACK_BUTTON-':
                    configWindowActive = False
                    title_window.UnHide()
                    configWindow.Close()
                    break

                if eventC == '-GOTO_STUDIO_BUTTON-':
                    studioWindowActive = False
                    configWindow.Close()
                    configWindowActive = False
                    event0 = '-CONTINUE_BUTTON-'
                    break


                if eventC == '-UPDATE_CONFIG-' and valuesC['-ROBOT_SIZE_X-'] != '' and valuesC['-ROBOT_SIZE_Y-'] !='':
                    if configRobot_rectangle is not None:
                        canvas.delete_figure(configRobot_rectangle)
                    robotSize_X = int(valuesC['-ROBOT_SIZE_X-']) * 18
                    robotSize_Y = int(valuesC['-ROBOT_SIZE_Y-']) * 18
                    configRobot_rectangle = canvas.draw_rectangle([173 - robotSize_X/2, 173 + robotSize_Y/2], [173 + robotSize_X/2, 173 - robotSize_Y/2], line_width=3)

                if eventC == '-FIELD_DD-':
                    fieldConfiguration = valuesC['-FIELD_DD-']




        if event0 is None or event0 == 'Exit:':
            break

        fieldSave = None
        if not studioWindowActive and event0 == '-CONTINUE_BUTTON-':
            title_window.Hide()
            studioWindowActive = True

            pathInfo = sg.Text('None', key='-PATH_INFO-', size=[20, 1], font='verdana')
            turnInfo = sg.Text('None', key='-TURN_INFO-', size=[20, 1], font='verdana')
            savesInfo = sg.Text('None', key='-SAVE_INFO-', size=[20, 1], font='verdana')

            # Each inch is five pixels
            field = sg.Graph(canvas_size=[720, 720], graph_bottom_left=[0, 0], graph_top_right=[720, 720],
                                 background_color='#BAB8B8', key='-FIELD-', enable_events=True)
            fieldSave_MASTER = field

            paths_tab = [[sg.Listbox(values=[], size=(50, 6), key='-PATH_LIST-')],
                         [sg.Button('Edit Path', key='-EDIT_PATH_BUTTON-', font='verdana'),
                          sg.Button('Round All', key='-ROUND_ALL_BUTTON-', font='verdana')],
                         [sg.Text('Selected Path:', font='verdana'), pathInfo],
                         [sg.Text('Start X', key='-START_X_TEXT-', font='verdana'),
                          sg.InputText(enable_events=True, size=[10, 1], key='-START_X_INPUT-', font='verdana'),
                          sg.Text('   Start Y', key='-START_Y_TEXT-', font='verdana'),
                          sg.InputText(enable_events=True, size=[10, 1], key='-START_Y_INPUT-', font='verdana')],
                         [sg.Text('Final X', key='-FINAL_X_TEXT-', font='verdana'),
                          sg.InputText(enable_events=True, size=[10, 1], key='-FINAL_X_INPUT-', font='verdana'),
                          sg.Text('   Final Y', key='-FINAL_Y_TEXT-', font='verdana'),
                          sg.InputText(enable_events=True, size=[10, 1], key='-FINAL_Y_INPUT-', font='verdana')],
                         [sg.Text('Velocity', font='verdana'), sg.InputText(enable_events=True, size=[10, 1], key='-VELOCITY_INPUT-', font='verdana')],
                         [sg.Button('Deselect', key='-DESELECT_BUTTON-', font='verdana')]]

            turns_tab = [[sg.Listbox(values=[], size=(50, 6), key='-TURN_LIST-', font='verdana')],
                         [sg.Button('Edit Turn', key='-EDIT_TURN_BUTTON-', font='verdana')],
                         [sg.Text('Selected Turn:', font='verdana'), turnInfo],
                         [sg.Text('Angle', key='-ANGLE_TEXT-', font='verdana'),
                          sg.InputText(enable_events=True, size=[10, 1], key='-ANGLE_INPUT-', font='verdana')]]

            saves_tab = [[sg.Listbox(values=[], size=(50, 4), key='-SAVES_LIST-', font='verdana')],
                         [sg.Button('Select Save', key='-SELECT_SAVE_BUTTON-', font='verdana')],
                          [sg.Text('Selected Turn:', font='verdana')]]

            editing_tabGroup = sg.TabGroup(
                layout=[[sg.Tab(layout=paths_tab, title='Paths', font='Verdana'), sg.Tab(layout=turns_tab, title='Turns', font='Verdana 10 bold')]])

            saves_tabGroup = sg.TabGroup(layout=[[sg.Tab(layout=saves_tab, title='Saves')]])

            main_column = [[sg.Button('Save Field', key='-SAVE_BUTTON-', font='verdana'), sg.Button('Load Field', key='-LOAD_BUTTON-', font='verdana')],
                           [sg.Button('Set Start Point', key='-START_POINT_BUTTON-', font='verdana')],
                           [sg.Button('Add Point', key='-ADD_POINT_BUTTON-', font='verdana'), sg.Button('Delete Point', key='-DELETE_POINT_BUTTON-', font='verdana')],
                           [sg.Button('Add Turn', key='-ADD_TURN_BUTTON-', font='verdana'), sg.Button('Delete Turn', key='-DELETE_TURN_BUTTON-', font='verdana')],
                           [sg.Button('Add Robot Operation', font='verdana')],
                           [sg.Button('Simulate Robot Run', key='-SIMULATE_BUTTON-', font='verdana')],
                           [sg.Text('\nEdit Menu:', font='verdana')],
                           [editing_tabGroup],
                           [sg.Text('Selected Drivetrain: ' + drivetrain[drivetrain.index('['): drivetrain.index(']') + 1], font='verdana')],
                           [sg.Button('Clear Field', key='-CLEAR_FIELD_BUTTON-', font='verdana')],
                           [sg.Button('Export Field', key='-EXPORT_BUTTON-', font='verdana')]]

            layout = [[sg.Text('Field Configuration: ' + fieldConfiguration, font='Verdana 16 bold')], [field, sg.Column(main_column)],
                      [sg.Button('Back', key='-BACK_BUTTON-', font='verdana'), sg.Button('Go to Configuration Menu', key='-GOTO_CONFIG_BUTTON-', font='verdana'),
                       sg.Button('Exit', font='verdana')]]
            studio_window = sg.Window('EXPERIMENTAL GUI', layout)

            studio_window.finalize()

            # Hide certain elements
            studio_window['-START_X_TEXT-'].hide_row()
            studio_window['-FINAL_X_TEXT-'].hide_row()
            studio_window['-VELOCITY_INPUT-'].hide_row()
            studio_window['-DESELECT_BUTTON-'].hide_row()
            studio_window['-ANGLE_TEXT-'].hide_row()

            for z in range(1, 31):
                field.draw_line([24 * z, 720], [24 * z, 0], 'light grey')
                field.draw_line([0, 24 * z], [720, 24 * z], 'light grey')
            for x in range(1, 6):
                field.draw_line([120 * x, 720], [120 * x, 0], 'black')
                field.draw_line([0, 120 * x], [720, 120 * x], 'black')

            if fieldConfiguration == 'FTC Skystone':
                field.draw_line([0,120], [120,120], width=6, color='red')
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

                field.draw_rectangle([241, 240],[261, 0], fill_color='yellow', line_width=0)
                for y in range(0, 7):
                    field.draw_line([241, y*40],[261, y*40], width=0.5)


        while True and studioWindowActive:  # Event Loop
            event1, values1 = studio_window.read()  # can also be written as event, values = window()

            # Print to console the event and values
            print('Event:')
            print(event1)
            print('Values:')
            print(values1)
            print()

            # Exit Condition
            if event1 is None or event1 == 'Exit':
                studio_window.close()
                title_window.close()
                break

            if event1 =='-GOTO_CONFIG_BUTTON-':
                studioWindowActive = False
                configWindowActive = False
                studio_window.Hide()
                changingWindow = True
                event0 = '-CONFIG_BUTTON-'
                print(str(event1))
                break


            # Back Condition
            if event1 is None or event1 == '-BACK_BUTTON-':
                studioWindowActive = False
                studio_window.Close()
                title_window.UnHide()
                fieldSave = field
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
                        studio_window['-PATH_INFO-'].update('Path #' + str(counter))
                        selectedPathNum = counter

            # Show the entry fields for editing the path
            if selectedPathNum is not None and not pathEditUpdated:
                studio_window['-START_X_TEXT-'].unhide_row()
                studio_window['-FINAL_X_TEXT-'].unhide_row()
                studio_window['-VELOCITY_INPUT-'].unhide_row()
                studio_window['-DESELECT_BUTTON-'].unhide_row()
                studio_window['-START_X_INPUT-'].update(value=convertedPoints[selectedPathNum - 1][0])
                studio_window['-START_Y_INPUT-'].update(value=convertedPoints[selectedPathNum - 1][1])
                studio_window['-FINAL_X_INPUT-'].update(value=convertedPoints[selectedPathNum][0])
                studio_window['-FINAL_Y_INPUT-'].update(value=convertedPoints[selectedPathNum][1])
                studio_window['-VELOCITY_INPUT-'].update(value=velocities[selectedPathNum - 1])
                pathEditUpdated = True
            # Change the values of a point based on what was entered into the entry field
            if pathEditUpdated:
                if event1 == '-START_X_INPUT-':
                    points[selectedPathNum - 1][0] = float(hf.clean_coordinates(values1['-START_X_INPUT-'])) * 5 + (
                                720 / 2)
                elif event1 == '-START_Y_INPUT-':
                    points[selectedPathNum - 1][1] = float(hf.clean_coordinates(values1['-START_Y_INPUT-'])) * 5 + (
                                720 / 2)
                elif event1 == '-FINAL_X_INPUT-':
                    points[selectedPathNum][0] = float(hf.clean_coordinates(values1['-FINAL_X_INPUT-'])) * 5 + (720 / 2)
                elif event1 == '-FINAL_Y_INPUT-':
                    points[selectedPathNum][1] = float(hf.clean_coordinates(values1['-FINAL_Y_INPUT-'])) * 5 + (720 / 2)
                elif event1 == '-VELOCITY_INPUT-':
                    velocities[selectedPathNum - 1] = float(hf.clean_coordinates(values1['-VELOCITY_INPUT-']))

            # Rounds all the points to the nearest inch
            if event1 == '-ROUND_ALL_BUTTON-':
                for i in range(0, len(convertedPoints)):
                    points[i][0] = round(convertedPoints[i][0]) * 5 + (720 / 2)
                    points[i][1] = round(convertedPoints[i][1]) * 5 + (720 / 2)

            # Deselect the current path
            if event1 == '-DESELECT_BUTTON-':
                selectedPathNum = None
            if selectedPathNum is None:
                studio_window['-PATH_INFO-'].update('None')
                studio_window['-START_X_TEXT-'].hide_row()
                studio_window['-FINAL_X_TEXT-'].hide_row()
                studio_window['-DESELECT_BUTTON-'].hide_row()
                studio_window['-VELOCITY_INPUT-'].hide_row()

            # Choose which turn to edit
            if event1 == '-EDIT_TURN_BUTTON-':
                counter = 0
                turnEditUpdated = False
                for t in turnStrings:
                    counter += 1
                    if len(values1['-TURN_LIST-']) > 0 and values1['-TURN_LIST-'][0] == t:
                        studio_window['-TURN_INFO-'].update('Turn #' + str(counter))
                        selectedTurnNum = counter

            if selectedTurnNum is None:
                studio_window['-ANGLE_TEXT-'].hide_row()
                studio_window['-TURN_INFO-'].update('None')
            # Show the entry fields for editing the turn
            if selectedTurnNum is not None and not turnEditUpdated:
                studio_window['-ANGLE_TEXT-'].unhide_row()
                studio_window['-ANGLE_INPUT-'].update(value=turns[selectedTurnNum - 1][1])
                turnEditUpdated = True
            # Change the angle value of a turn based on what was entered into the entry field
            if turnEditUpdated:
                if event1 == '-ANGLE_INPUT-':
                    turns[selectedTurnNum - 1][1] = float(hf.clean_coordinates(values1['-ANGLE_INPUT-']))

            # Select start point and draw the circle for it and add it to points
            if event1 == '-START_POINT_BUTTON-':
                selectedOperation = 'selectingStartPoint'
            if selectedOperation == 'selectingStartPoint':
                if event1 == '-FIELD-':
                    field.delete_figure(startPoint_circle)
                    startPoint_circle = field.draw_circle([values1['-FIELD-'][0], values1['-FIELD-'][1]], 5)
                    if len(points) > 0:
                        points[0] = ([values1['-FIELD-'][0], values1['-FIELD-'][1]])
                    else:
                        points.append([values1['-FIELD-'][0], values1['-FIELD-'][1]])
                    startHeading = float(hf.clean_coordinates(sg.PopupGetText(
                        message='Enter start heading, 0 is straight up, 90 is to the right, -90 is to the left',
                        title='Heading selection')))
                    selectedOperation = None

            # Select next point and and it to list of points
            if event1 == '-ADD_POINT_BUTTON-' and len(points) > 0:
                selectedOperation = 'addingPoint'
            if selectedOperation == 'addingPoint':
                if event1 == '-FIELD-':
                    points.append([values1['-FIELD-'][0], values1['-FIELD-'][1]])
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
                        if abs(values1['-FIELD-'][0] - p[0]) < 10 and abs(values1['-FIELD-'][1] - p[1]) < 10:
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
                        if abs(values1['-FIELD-'][0] - points[t[0]][0]) < 10 and abs(values1['-FIELD-'][1] - points[t[0]][1]) < 10:
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
                        if abs(values1['-FIELD-'][0] - points[i][0]) < 10 and abs(values1['-FIELD-'][1] - points[i][1]) < 10 and allowPointToBeSelected:
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
                                                                       angle2=startHeading, degrees_per_second=45,
                                                                       frames_per_second=60)
                for i in range(1, len(points)):
                    deltas = hf.calculate_movement_per_frame(points[i - 1], points[i],
                                                             inches_per_second=velocities[i - 1], frames_per_second=60,
                                                             pixels_per_inch=5)
                    num_movements = math.sqrt(
                        (points[i][0] - points[i - 1][0]) ** 2 + (points[i][1] - points[i - 1][1]) ** 2) / math.hypot(
                        deltas[0], deltas[1])
                    x = points[i - 1][0]
                    y = points[i - 1][1]
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
                            rot_deltas = hf.calculate_rotation_per_frame(points=robotPolygonPoints, angle1=angle1,
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
                                            y + rot_deltas_final[0][1][j]]  # Bottom right corner and go clockwise
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
                                robot_point = field.draw_point(point=robotLinePoints[0], color='yellow', size=15)
                                studio_window.refresh()
                                sleepTime = 1 / 60 - (time.time() - start_time)
                                if sleepTime < 0:
                                    sleepTime = 0
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
                        robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black', line_width='3',
                                                           fill_color='')
                        robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                        if startHeading == 0 and rot_deltas_final == [[[45], [-45]], [[-45], [-45]], [[-45], [45]],
                                                                      [[45], [45]]]:
                            robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0), ((robotCTr[1] + robotCTl[1]) / 2.0)]
                        robot_point = field.draw_point(point=robotPoint, color='yellow', size=15)
                        studio_window.refresh()
                        sleepTime = 1 / 60 - (time.time() - start_time)
                        if sleepTime < 0:
                            sleepTime = 0
                        time.sleep(sleepTime)
                selectedOperation = None

            if event1 == '-EXPORT_BUTTON-':
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
                        sg.Popup('Export Successful!')
                else:
                    sg.Popup('No Paths to Export')

            if event1 == '-SAVE_BUTTON-':
                save_name = ''
                while save_name == '':
                    save_name = sg.PopupGetText('Name:')
                if save_name is not None:
                    save_location = sg.PopupGetFolder('', no_window=True)
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
                choice = sg.PopupYesNo('Do you want to load a save?\nYou will lose any unsaved progress if you do so.')
                if choice == 'Yes':
                    points.clear()
                    turns.clear()
                    velocities.clear()
                    save_location = sg.PopupGetFile('Hello', no_window=True, file_types=(("Auton Files", "*.auton"),))
                    save_file = open(save_location, 'r')
                    num_points = int(save_file.readline())
                    for i in range(num_points):
                        line = save_file.readline().split()
                        points.append([int(line[0]), int(line[1])])
                        velocities.append(defaultVelocity)
                    num_turns = int(save_file.readline())
                    for i in range(num_turns):
                        line = save_file.readline().split()
                        turns.append([int(line[0]), int(line[1])])
                    save_file.close()

            # Add points and turns to list of paths and turns, then display them in the path and turn list
            pathStrings = []
            convertedPoints = hf.convert_coordinates_to_inches(points, pixels_per_inch=5, field_length_inches=144)
            heading = startHeading
            prevTurn = None
            for i in range(1, len(points)):
                for t in turns:
                    if t[0] == i - 1:
                        if prevTurn is None:
                            heading = startHeading
                        else:
                            heading = prevTurn[1]
                    prevTurn = t
                pathStrings.append(
                    'Path #' + str(i) + ': ' + hf.generate_path_string(convertedPoints[i - 1], convertedPoints[i],
                                                                       velocities[i - 1], heading))
            studio_window['-PATH_LIST-'].update(values=pathStrings)
            turnStrings = []
            turns = hf.sort_turns(turns)
            for i in range(0, len(turns)):
                turnStrings.append('Turn #' + str(i + 1) + ": " + hf.generate_turn_string(turns[i], convertedPoints))
            studio_window['-TURN_LIST-'].update(values=turnStrings)

            # Draw turn indicators
            for i in range(len(turnIndicator_circles)):
                field.delete_figure(turnIndicator_circles[i])
                field.delete_figure(turnIndicator_text[i])
            for i in range(0, len(turns)):
                if len(turnIndicator_circles) < i + 1:
                    turnIndicator_circles.append(None)
                    turnIndicator_text.append(None)
                turnIndicator_circles[i] = field.draw_circle(points[turns[i][0]], 5, fill_color='black')
                turnIndicator_text[i] = field.draw_text(text=str(turns[i][1]) + '°',
                                                        location=[points[turns[i][0]][0] + 10,
                                                                  points[turns[i][0]][1] + 10], color='dark blue')

            # Draw robot on the field and ensures the robot cannot be magically clipping through
            # the field walls (robot starts touching field wall if outside boundary)
            if len(points) > 0:
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
                                                                       angle2=startHeading, degrees_per_second=45,
                                                                       frames_per_second=60)
                robotCBr = [points[0][0] + rot_deltas_final[0][0][-1],
                            points[0][1] + rot_deltas_final[0][1][-1]]  # Bottom right corner and go clockwise
                robotCBl = [points[0][0] + rot_deltas_final[1][0][-1], points[0][1] + rot_deltas_final[1][1][-1]]
                robotCTl = [points[0][0] + rot_deltas_final[2][0][-1], points[0][1] + rot_deltas_final[2][1][-1]]
                robotCTr = [points[0][0] + rot_deltas_final[3][0][-1], points[0][1] + rot_deltas_final[3][1][-1]]
                robotPolygonPoints = [robotCBr, robotCBl, robotCTl, robotCTr]
                robot_polygon = field.draw_polygon(robotPolygonPoints, line_color='black', line_width='3',
                                                   fill_color='')
                robotPoint = [((robotCTr[0] + robotCBr[0]) / 2.0), ((robotCTr[1] + robotCBr[1]) / 2.0)]
                if startHeading == 0:
                    robotPoint = [((robotCTr[0] + robotCTl[0]) / 2.0), ((robotCTr[1] + robotCTl[1]) / 2.0)]
                robot_point = field.draw_point(point=robotPoint, color='yellow', size=15)

                # Draw lines between all points
                print(points)
                if len(points) > 0:
                    field.delete_figure(startPoint_circle)
                    startPoint_circle = field.draw_circle(points[0], 5)
                field.delete_figure(startPoint_line)
                if len(points) > 1:
                    lineColor = 'black'
                    if selectedPathNum == 1:
                        lineColor = 'yellow'
                    startPoint_line = field.draw_line(points[0], points[1], color=lineColor, width=2.0)
                for pl in point_lines:
                    field.delete_figure(pl)
                for i in range(2, len(points)):
                    lineColor = 'black'
                    if selectedPathNum == i:
                        lineColor = 'yellow'
                    if len(point_lines) < i - 1:
                        point_lines.append(None)
                    point_lines[i - 2] = (field.draw_line(points[i - 1], points[i], color=lineColor, width=2.0))

    export_file.close()
    title_window.close()
