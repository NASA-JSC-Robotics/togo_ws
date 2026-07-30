from functools import partial
import math

# ROS
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

# status message types
from clearpath_platform_msgs.msg import StopStatus
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool

# status state
from togo_status_handler.status_state import StatusState


##############################
# STATUS NODE HELPER CLASSES #
##############################


class SavedStatusMessage:
    """Class to capture a message that may or may not be updated each cycle.
    Allows the status node to track whether messages have stopped being received.
    """

    def __init__(self, msg_type):
        """Constructor for Saved Status Message.

        Args:
            msg_type (any message type): the type of the emssage to store; must be default constructible
        """

        self.msg_type = msg_type
        self.msg = msg_type()
        self.updated = False

    def update_msg(self, msg):
        """Update status message with new message content.

        Args:
            msg (msg_type): New message content

        Raises:
            TypeError: Attempt to update a message with a message of a different type
        """

        # check type of incoming message
        if self.msg_type != type(msg):
            raise TypeError(
                "Expected to update a message of type "
                + str(self.msg_type)
                + " but received a message of type "
                + str(type(msg))
            )

        # update message content
        self.msg = msg
        self.updated = True

        return

    def reset_msg_update(self):
        """Reset the update flag in preparation for the next cycle."""

        self.updated = False

        return


class StatusSubscriptionSet:
    """Class to capture a set of SavedStatusMessage types.
    Adds convenience functions for working with the full set.
    """

    def __init__(self, msgs: dict[str, SavedStatusMessage]):
        """Constructor for Status Subscription Set.

        Args:
            msgs (dict[str, SavedStatusMessage]): dictionary of status descriptors to SavedStatusMessage
        """

        self.msgs = msgs

    def all_updated(self) -> bool:
        """Checks if all SavedStatusMessages in the set are updated.

        Returns:
            bool: flag indicating whether all status messages are updated
        """

        return all([self.msgs[k].updated for k in self.msgs])

    def reset_update(self):
        """Resets all SavedStatusMessage updates."""

        for k in self.msgs:
            self.msgs[k].reset_msg_update()

        return


#################################
# STATUS TUI BACKEND NODE CLASS #
#################################


class StatusTUIBackendNode(Node):
    """Determines simplified Togo system state from a set of Clearpath subscriptions."""

    #######################
    # STATE CUTOFF VALUES #
    #######################
    # based on Togo Standard Operating Procedures and Clearpath Husky A300 AMP documentation

    # battery percentages
    BATTERY_LOW_PERCENTAGE = 0.2
    BATTERY_HIGH_PERCENTAGE = 0.9
    # temperature cutoffs
    TEMPERATURE_LOW_VALUE = 10.0
    TEMPERATURE_HIGH_VALUE = 45.0

    def __init__(self, display=None):
        """Constructor for Status TUI Backend Node.

        Args:
            display (Any, optional): Any class with an update function that can take a StatusState message or None.
                If None, the current Togo state will be written to the terminal.
                Defaults to None.
        """

        # initialize parent class
        super().__init__("status_tui_backend_node")

        # set display
        self.display = display
        # set status
        self.status = StatusState()
        # create status subscription set
        self.state_set = StatusSubscriptionSet(
            {
                "battery_status": SavedStatusMessage(BatteryState),
                "stop_status": SavedStatusMessage(StopStatus),
                "estop_status": SavedStatusMessage(Bool),
                "cmd_vel": SavedStatusMessage(TwistStamped),
            }
        )

        # set up QoS profile
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # status subscriptions
        # NOTE: we will rely on the namespace being set from the command line
        # just in case the namespacing on these core Clearpath nodes changes
        # NOTE: partial binds a function argument so the callback knows what message to update
        self.battery_sub = self.create_subscription(
            BatteryState, "platform/bms/state", partial(self.update_status_msg_cb, "battery_status"), qos
        )
        self.stop_sub = self.create_subscription(
            StopStatus, "platform/mcu/status/stop", partial(self.update_status_msg_cb, "stop_status"), qos
        )
        self.estop_sub = self.create_subscription(
            Bool, "platform/emergency_stop", partial(self.update_status_msg_cb, "estop_status"), qos
        )
        self.cmd_vel_sub = self.create_subscription(
            TwistStamped, "/platform_velocity_controller/cmd_vel", partial(self.update_status_msg_cb, "cmd_vel"), qos
        )

        # create timer to drive update cycle
        self.timer = self.create_timer(1.0, self.timer_callback)

        # if display provided, set logger for the display as well
        if self.display:
            self.display.set_logger(self.get_logger())

    #########################
    # SUBSCRIPTION CALLBACK #
    #########################

    def update_status_msg_cb(self, status_state: str, msg):
        """Callback function to store a subscribed status message.

        Args:
            status_state (str): status descriptor; must be one of the keys in the subscription set
            msg (any message type): incoming message
        """
        self.state_set.msgs[status_state].update_msg(msg)

        return

    ##################
    # TIMER CALLBACK #
    ##################

    def timer_callback(self):
        """Timer callback to compute and display robot status."""

        self.compute_state()
        self.display_status()

        return

    #############################
    # STATUS NODE FUNCTIONALITY #
    #############################

    def compute_state(self):
        """Compute the current aggregated robot state from the latest received status messages."""

        # compute all state information
        self.compute_battery_state()
        self.compute_robot_state()
        self.compute_driving_state()

        # reset update for all subscriptions since we have processed the current messages
        self.state_set.reset_update()

        return

    def compute_battery_state(self):
        """Compute the current battery and charging states."""

        # check for updated data
        if not self.state_set.msgs["battery_status"].updated:
            # no message received
            self.status.battery_state = StatusState.BATTERY_STATE_NO_COMM
            self.status.temperature_state = StatusState.TEMPERATURE_STATE_NO_COMM
            self.status.charging_state = StatusState.CHARGING_STATE_NO_COMM
            self.status.battery_percent = math.nan
            self.status.battery_voltage = math.nan
            self.status.battery_amps = math.nan
            self.status.battery_temp = math.nan
            return

        # set battery state values
        self.status.battery_percent = int(round(self.state_set.msgs["battery_status"].msg.percentage, 2) * 100)
        self.status.battery_voltage = self.state_set.msgs["battery_status"].msg.voltage
        self.status.battery_amps = self.state_set.msgs["battery_status"].msg.current
        self.status.battery_temp = self.state_set.msgs["battery_status"].msg.temperature

        # set battery status based on charge
        if self.state_set.msgs["battery_status"].msg.power_supply_health != BatteryState.POWER_SUPPLY_HEALTH_GOOD:
            # faulted
            self.status.battery_state = StatusState.BATTERY_STATE_FAULTED
        elif self.status.battery_percent <= self.BATTERY_LOW_PERCENTAGE * 100:
            # low battery
            self.status.battery_state = StatusState.BATTERY_STATE_LOW
        elif self.status.battery_percent > self.BATTERY_HIGH_PERCENTAGE * 100:
            # full
            self.status.battery_state = StatusState.BATTERY_STATE_FULL
        else:
            # ok
            self.status.battery_state = StatusState.BATTERY_STATE_OK

        # set temperature status
        if self.status.battery_temp < self.TEMPERATURE_LOW_VALUE:
            # low temp
            self.status.temperature_state = StatusState.TEMPERATURE_STATE_LOW
        elif self.status.battery_temp > self.TEMPERATURE_HIGH_VALUE:
            # high temp
            self.status.temperature_state = StatusState.TEMPERATURE_STATE_HIGH
        else:
            # ok
            self.status.temperature_state = StatusState.TEMPERATURE_STATE_OK

        # set charging state
        if self.state_set.msgs["battery_status"].msg.power_supply_status == BatteryState.POWER_SUPPLY_STATUS_CHARGING:
            # charging
            self.status.charging_state = StatusState.CHARGING_STATE_ACTIVE
        else:
            # not charging
            self.status.charging_state = StatusState.CHARGING_STATE_INACTIVE

        return

    def compute_robot_state(self):
        """Compute the current robot state."""

        # check for updated data
        if not (self.state_set.msgs["estop_status"].updated and self.state_set.msgs["stop_status"].updated):
            # no messages received
            self.status.robot_state = StatusState.ROBOT_STATE_NO_COMM
            return

        # check estop state
        if self.state_set.msgs["stop_status"].msg.needs_reset:
            # reset
            self.status.robot_state = StatusState.ROBOT_STATE_NEEDS_RESET
        elif self.state_set.msgs["estop_status"].msg.data:
            # estopped   
            self.status.robot_state = StatusState.ROBOT_STATE_ESTOPPED
        else:
            # running
            self.status.robot_state = StatusState.ROBOT_STATE_RUNNING

        return

    def compute_driving_state(self):
        """Compute the current driving state."""

        # check for updated data
        if not self.state_set.msgs["cmd_vel"].updated:
            # no message received
            self.status.driving_state = StatusState.DRIVING_STATE_NO_COMM
            return

        # check for non-zero command
        linear = self.state_set.msgs["cmd_vel"].msg.twist.linear
        angular = self.state_set.msgs["cmd_vel"].msg.twist.angular
        cmd = [linear.x, linear.y, linear.z, angular.x, angular.y, angular.z]
        if all([c == 0.0 for c in cmd]):
            # all zero, not driving
            self.status.driving_state = StatusState.DRIVING_STATE_OFF
        else:
            # driving
            self.status.driving_state = StatusState.DRIVING_STATE_ON

        return

    def display_status(self):
        """Update the display with the current robot status."""

        if self.display:
            # update the display with the current status
            self.display.update(self.status)
        else:
            # no display provided, write status to terminal
            self.get_logger().info(str(self.status))

        return
