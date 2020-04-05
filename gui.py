from enums import TitleEvents

import PySimpleGUI as pygui

if __name__ == '__main__':

    fieldSave_MASTER = None

    pygui.theme('Dark Green')
    logo = pygui.Image('resources/autonStudioLogo.png')
    menu_column = [
        pygui.Text('\n\n'),
        pygui.Button('Click to Continue to Studio', key='-CONTINUE_BUTTON-', font='verdana'),
        pygui.Button('Add Configuration', key='-CONFIG_BUTTON-', font='Verdana'),
        pygui.Listbox(
            [
               'Mechanum with Odometry',
               'Mechanum without Odometry',
               'H-Drive with Odometry',
               'H-Drive without Odometry'
           ],
            enable_events=True, key=TitleEvents.SELECT_DRIVETRAIN, size=(25, 4),
            default_values='Mechanum with Odometry', font='verdana'
       )
    ]

    layout2 = [[pygui.Text('Welcome to Auton Studio', text_color='Black', font='Verdana 20 bold', justification='center',
                        size=[32, 1])], [logo, pygui.Column(menu_column)]]

    title_window = pygui.Window('Auton Studio', layout2)

    while True:
        titleEvent, titleValues = title_window.read()