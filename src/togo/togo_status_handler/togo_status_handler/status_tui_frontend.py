############################
# EXAMPLE STATUS RENDERING #
############################

"""
           Togo Status

-------
|     |   ___              ___    -->
|     |--------------------------
|     | _BAT_ 100% 28.0V 10.0A  |
|     |                         |
|     | _TMP_      72.0C  HOT   | front
|     |                         |
|     | _CHG_                   |
|     |--------------------------
|     |   ___              ___    -->
-------
"""

import curses
from togo_status_handler.status_state import StatusState

# See documentation for curses here: https://docs.python.org/3/library/curses.html

#################################
# STATUS DISPLAY HELPER CLASSES #
#################################


class StrStatusFrontend:
    """String status to draw at a position."""

    def __init__(self, screen: curses.window, row: int, col: int, content: str = ""):
        """Constructor for String Status Frontend.

        Args:
            screen (curses.window): the screen for drawing content
            row (int): row to draw at
            col (int): column to draw at
            content (str, optional): Initial string content. Defaults to "".
        """
        self.screen = screen
        self.row = row
        self.col = col
        self.content = content

    def draw(self, attributes):
        """Draw the content with the provided color attributes.

        Args:
            attributes (int): curses color attribute value
        """

        self.screen.addstr(self.row, self.col, self.content, attributes)

        return


class WheelStatusFrontend(StrStatusFrontend):
    """Specialized string status for Togo's wheel status."""

    def __init__(self, screen, row, col, size: int = 3):
        super().__init__(screen, row, col)
        self.size = size

    def draw(self, attributes):
        """Draw the wheel state with the provided color attributes.

        Args:
            attributes (int): curses color attribute
        """

        self.screen.addstr(self.row, self.col, (" " * self.size), attributes)

        return


#############################
# STATUS TUI FRONTEND CLASS #
#############################


class StatusTUIFrontend:
    """Text-based User Interface (TUI) for Togo status."""

    ######################
    # STATIC DEFINITIONS #
    ######################

    # define body shape
    ROBOT = (
        "-------",
        "|     |",
        "|     |--------------------------",
        "|     |                         |",
        "|     |                         |",
        "|     |                         | front",
        "|     |                         |",
        "|     |                         |",
        "|     |--------------------------",
        "|     |",
        "-------",
    )

    # mast positions
    MAST_START_ROW = 2
    MAST_END_ROW = MAST_START_ROW + len(ROBOT)
    MAST_START_COL = 4
    MAST_END_COL = MAST_START_COL + len(ROBOT[0])
    # body positions
    BODY_START_ROW = MAST_START_ROW + 2
    BODY_END_ROW = MAST_END_ROW - 2
    BODY_START_COL = MAST_START_COL + len(ROBOT[0])
    BODY_END_COL = MAST_START_COL + len(ROBOT[2])
    # wheel spacing from edges of body
    WHEEL_SPACING = 3
    # wheel size
    WHEEL_SIZE = 3

    #####################################
    # CLASS INITIALIZATION AND DELITION #
    #####################################

    def __init__(self):
        """Constructor for Status TUI Frontend."""

        # create the curses screen
        self.screen = curses.initscr()
        # initialize colors
        curses.start_color()
        # do not write input characters
        curses.noecho()
        # make cursor invisible
        curses.curs_set(0)
        # define color pairings (pairing-num, FG, BG)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

        # dictionary of color name to pairing attributes (based on pairings defined above)
        # NOTE: use bitwise OR operator to create a mask of color attributes
        self.colors = {
            "grey": (curses.color_pair(1) | curses.A_DIM),  # dim mode on white
            "white": (curses.color_pair(1) | curses.A_BOLD),  # bold mode
            "black": curses.color_pair(2),
            "red": curses.color_pair(3),
            "yellow": curses.color_pair(4),
            "green": curses.color_pair(5),
            "boldgreen": (curses.color_pair(5) | curses.A_BOLD),
            "blue": curses.color_pair(6),
        }

        # create status objects to draw
        self.status_objects = {
            # wheels
            "left_rear_wheel": WheelStatusFrontend(
                self.screen, self.BODY_START_ROW - 1, self.MAST_END_COL + self.WHEEL_SPACING, self.WHEEL_SIZE
            ),
            "left_front_wheel": WheelStatusFrontend(
                self.screen,
                self.BODY_START_ROW - 1,
                self.BODY_END_COL - self.WHEEL_SPACING - self.WHEEL_SIZE,
                self.WHEEL_SIZE,
            ),
            "right_rear_wheel": WheelStatusFrontend(
                self.screen, self.BODY_END_ROW, self.MAST_END_COL + self.WHEEL_SPACING, self.WHEEL_SIZE
            ),
            "right_front_wheel": WheelStatusFrontend(
                self.screen,
                self.BODY_END_ROW,
                self.BODY_END_COL - self.WHEEL_SPACING - self.WHEEL_SIZE,
                self.WHEEL_SIZE,
            ),
            # battery info
            "battery_light": StrStatusFrontend(self.screen, self.BODY_START_ROW + 1, self.BODY_START_COL + 1, " BAT "),
            "battery_stats": StrStatusFrontend(
                self.screen,
                self.BODY_START_ROW + 1,
                self.BODY_START_COL + 7,  # space for light (1+len(" BAT ")) and stats start (+1)
                "",
            ),
            # battery temperature
            "temp_light": StrStatusFrontend(self.screen, self.BODY_START_ROW + 3, self.BODY_START_COL + 1, " TMP "),
            "temp_stats": StrStatusFrontend(
                self.screen,
                self.BODY_START_ROW + 3,
                self.BODY_START_COL
                + 12,  # space for light (1+len(" TMP ")) and battery percent (1+len("100%")) and stats start (+1)
                "",
            ),
            # charging indicator
            "charge_light": StrStatusFrontend(self.screen, self.BODY_START_ROW + 5, self.BODY_START_COL + 1, " CHG "),
            # driving indicators
            "drive_left": StrStatusFrontend(self.screen, self.BODY_START_ROW - 1, self.BODY_END_COL + 1, "-->"),
            "drive_right": StrStatusFrontend(self.screen, self.BODY_END_ROW, self.BODY_END_COL + 1, "-->"),
        }

        # initialize update counter; used to simulate blinking
        self.update_count = 0

        # draw initial robot state
        self.draw_robot()

    def __del__(self):
        """Curses cleanup. Needed to reset the terminal."""

        curses.echo()
        curses.endwin()

    ##########
    # LOGGER #
    ##########

    def set_logger(self, logger):
        """Allow client to inject a ROS logger.

        Args:
            logger (RCL logger): ROS logger
        """

        self.logger = logger

        return

    ######################
    # DRAW INITIAL ROBOT #
    ######################

    def draw_robot(self):
        """Draw initial robot state."""

        # clear the screen
        self.screen.clear()

        # status title
        self.screen.addstr(0, 15, "Togo Status", (self.colors["grey"] | curses.A_UNDERLINE))

        # draw robot body
        row = self.MAST_START_ROW
        for line in self.ROBOT:
            self.screen.addstr(row, self.MAST_START_COL, line, self.colors["grey"])
            row += 1

        # draw status objects
        self.update_all_wheel_lights("grey")
        self.update_battery("grey")
        self.update_temperature("grey")
        self.update_charging("grey")
        self.update_driving("black")  # black on black effectively hides the object

        # tell curses to display what has been drawn
        self.screen.refresh()

        return

    ##################
    # UPDATE DRAWING #
    ##################

    def update(self, state: StatusState):
        """Main frontend update callback, triggered by the client.

        Args:
            state (StatusState): incoming status message
        """

        # increment update count
        self.update_count += 1

        # update wheels based on robot state
        if state.robot_state == StatusState.ROBOT_STATE_ESTOPPED:
            # blinking red
            self.update_all_wheel_lights("red", is_blinking=True)
        elif state.robot_state == StatusState.ROBOT_STATE_NEEDS_RESET:
            # alternating blinking red; opposite corners should blink together
            self.update_wheel_light("left_rear_wheel", "red", is_blinking=True, blink_parity=0)
            self.update_wheel_light("left_front_wheel", "red", is_blinking=True, blink_parity=1)
            self.update_wheel_light("right_rear_wheel", "red", is_blinking=True, blink_parity=1)
            self.update_wheel_light("right_front_wheel", "red", is_blinking=True, blink_parity=0)
        elif state.robot_state == StatusState.ROBOT_STATE_RUNNING:
            # front white, rear red
            self.update_wheel_light("left_rear_wheel", "red")
            self.update_wheel_light("left_front_wheel", "white")
            self.update_wheel_light("right_rear_wheel", "red")
            self.update_wheel_light("right_front_wheel", "white")
        else:  # no comm
            self.update_all_wheel_lights("grey")

        # update battery state
        if state.battery_state == StatusState.BATTERY_STATE_LOW:
            self.update_battery("yellow")
        elif state.battery_state == StatusState.BATTERY_STATE_OK:
            self.update_battery("green")
        elif state.battery_state == StatusState.BATTERY_STATE_FULL:
            self.update_battery("blue")
        elif state.battery_state == StatusState.BATTERY_STATE_FAULTED:
            self.update_battery("red")
        else:  # no comm
            self.update_battery("grey")

        self.update_battery_stats(state)

        # update temperature state
        if state.temperature_state == StatusState.TEMPERATURE_STATE_LOW:
            self.update_temperature("red")
        elif state.temperature_state == StatusState.TEMPERATURE_STATE_OK:
            self.update_temperature("green")
        elif state.temperature_state == StatusState.TEMPERATURE_STATE_HIGH:
            self.update_temperature("red")
        else:  # no comm
            self.update_temperature("grey")

        self.update_temperature_stats(state)

        # update charging state
        if state.charging_state == StatusState.CHARGING_STATE_INACTIVE:
            self.update_charging("black")
        elif state.charging_state == StatusState.CHARGING_STATE_ACTIVE:
            self.update_charging("green")
        else:  # no comm
            self.update_charging("grey")

        # update driving state
        if state.driving_state == StatusState.DRIVING_STATE_OFF:
            self.update_driving("yellow")
        elif state.driving_state == StatusState.DRIVING_STATE_ON:
            self.update_driving("boldgreen", is_blinking=True)
        else:  # no comm
            self.update_driving("black")

        # display what has been drawn
        self.screen.refresh()

        return

    ###################################
    # UPDATE DRAWING HELPER FUNCTIONS #
    ###################################

    def set_blinking_color(self, color_attributes: int, is_blinking: bool, blink_parity: int = 0) -> int:
        """Sets color attributes based on blinking status.
        Returned color attribute will either be what is provided or black-on-black.

        Args:
            attributes (int): curses color attribute
            is_blinking (bool): flag indicating blinking
            blink_parity (int, optional): blinking parity, either 0 or 1. Defaults to 0. Allows alternating blinking objects.

        Returns:
            int: color attributes adjusted based on blinking status

        Raises:
            ValueError: provided parity is not 0 or 1
        """

        # check parity
        if (blink_parity != 0) and (blink_parity != 1):
            raise ValueError("Blink parity must be 0 or 1, given " + str(blink_parity))

        # set color attributes based on blinking and parity
        if is_blinking and (self.update_count % 2 == blink_parity):
            # return black-on-black to simulate blinking
            return self.colors["black"]

        # otherwise, return given color attributes
        return color_attributes

    def update_wheel_light(self, wheel_name: str, color: str, is_blinking: bool = False, blink_parity: int = 0):
        """Draws a wheel light status object.

        Args:
            wheel_name (str): wheel name, corresponding to object key in status_objects dictionary
            color (str): color name, corresponding to color preset key in colors dictionary
            is_blinking (bool, optional): flag indicating blinking. Defaults to False.
            blink_parity (int, optional): blinking parity, either 0 or 1. Defaults to 0. Allows alternating blinking objects.

        Raises:
            ValueError: unknown wheel_name or color
        """

        # check wheel name
        if wheel_name not in self.status_objects:
            raise ValueError(
                "Unknown wheel object " + wheel_name + "; expected one of " + str(list(self.status_objects.keys()))
            )
        # check color
        if color not in self.colors:
            raise ValueError("Unknown color " + color + "; expected one of " + str(list(self.colors.keys())))

        # update color based on blinking status
        color_attributes = self.set_blinking_color((self.colors[color] | curses.A_REVERSE), is_blinking, blink_parity)

        # draw wheel object
        self.status_objects[wheel_name].draw(color_attributes)

        return

    def update_all_wheel_lights(self, color: str, is_blinking: bool = False):
        """Draw all wheel light status objects.

        Args:
            color (str): color name, corresponding to color preset key in colors dictionary
            is_blinking (bool, optional): flag indicating blinking. Defaults to False.

        Raises:
            ValueError: unknown color
        """

        # set all wheels to same color and blinking status
        self.update_wheel_light("left_rear_wheel", color, is_blinking)
        self.update_wheel_light("left_front_wheel", color, is_blinking)
        self.update_wheel_light("right_rear_wheel", color, is_blinking)
        self.update_wheel_light("right_front_wheel", color, is_blinking)

        return

    def update_battery(self, color: str):
        """Draw battery light status object.

        Args:
            color (str): color name, corresponding to color preset key in colors dictionary

        Raises:
            ValueError: unknown color
        """

        # check color
        if color not in self.colors:
            raise ValueError("Unknown color " + color + "; expected one of " + str(list(self.colors.keys())))

        # draw battery light
        self.status_objects["battery_light"].draw(self.colors[color] | curses.A_REVERSE)

        return

    def update_battery_stats(self, status_msg: StatusState):
        """Draw battery stats object.

        Args:
            status_msg (StatusState): status message containing battery stats
        """

        # create content string
        stats_content = (
            f"{status_msg.battery_percent:>3.0f}% {status_msg.battery_voltage:>4.1f}V {status_msg.battery_amps:>4.1f}A"
        )
        # set content
        self.status_objects["battery_stats"].content = stats_content

        # draw battery stats
        self.status_objects["battery_stats"].draw(self.colors["white"])

        return

    def update_temperature(self, color: str):
        """Draw temperature light status object.

        Args:
            color (str): color name, corresponding to color preset key in colors dictionary

        Raises:
            ValueError: unknown color
        """

        # check color
        if color not in self.colors:
            raise ValueError("Unknown color " + color + "; expected one of " + str(list(self.colors.keys())))

        # draw temperature light
        self.status_objects["temp_light"].draw(self.colors[color] | curses.A_REVERSE)

        return

    def update_temperature_stats(self, status_msg: StatusState):
        """Draw temperature stats object.

        Args:
            status_msg (StatusState): status message containing battery temperature stats
        """

        # create content string
        stats_content = f"{status_msg.battery_temp:>4.1f}C"
        if status_msg.temperature_state == StatusState.TEMPERATURE_STATE_HIGH:
            stats_content += "  HOT"
        elif status_msg.temperature_state == StatusState.TEMPERATURE_STATE_LOW:
            stats_content += "  COLD"
        else:  # nothing to report, be sure to overwrite where HOT/COLD were written
            stats_content += "      "
        # set content
        self.status_objects["temp_stats"].content = stats_content

        # draw temperature stats
        self.status_objects["temp_stats"].draw(self.colors["white"])

        return

    def update_charging(self, color: str):
        """Draw charging light status object.

        Args:
            color (str): color name, corresponding to color preset key in colors dictionary

        Raises:
            ValueError: unknown color
        """

        # check color
        if color not in self.colors:
            raise ValueError("Unknown color " + color + "; expected one of " + str(list(self.colors.keys())))

        # draw charging light
        self.status_objects["charge_light"].draw(self.colors[color] | curses.A_REVERSE)

        return

    def update_driving(self, color: str, is_blinking: bool = False):
        """Draw driving status objects.

        Args:
            color (str): color name, corresponding to color preset key in colors dictionary
            is_blinking (bool, optional): flag indicating blinking. Defaults to False.

        Raises:
            ValueError: unknown color
        """

        # check color
        if color not in self.colors:
            raise ValueError("Unknown color " + color + "; expected one of " + str(list(self.colors.keys())))

        # update color based on blinking status
        color_attributes = self.set_blinking_color(self.colors[color], is_blinking)

        # draw driving lights
        self.status_objects["drive_left"].draw(color_attributes)
        self.status_objects["drive_right"].draw(color_attributes)

        return
