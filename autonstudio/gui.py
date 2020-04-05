from enums import TitleEvents

import PySimpleGUI as pygui


def main() -> None:
    """
    The mainloop for the entire application, taking in events and processing GUI logic.
    """

    pygui.theme('Dark Green')
    menu_column = [
        [pygui.Text('\n\n')],
        [pygui.Button('Click to Continue to Studio', key='-CONTINUE_BUTTON-', font='verdana')],
        [pygui.Button('Add Configuration', key='-CONFIG_BUTTON-', font='Verdana')],
        [pygui.Listbox(
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
        [pygui.Text('Welcome to Auton Studio', text_color='Black', font='Verdana 20 bold', justification='center',
                   size=[32, 1])],
        [pygui.Image('resources/autonStudioLogo.png'), pygui.Column(menu_column)],
    ]

    titleWindow = pygui.Window('Auton Studio', titleLayout)

    while True:
        titleEvent, titleValues = titleWindow.read()

if __name__ == "__main__":
    main()