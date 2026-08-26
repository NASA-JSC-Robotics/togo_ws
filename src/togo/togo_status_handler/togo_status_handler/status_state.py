# Copyright (c) 2026, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
# All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import math


class StatusState:
    """Class for gathering high-level state information."""

    ##########################
    # STATUS STATE CONSTANTS #
    ##########################

    # robot state
    ROBOT_STATE_NO_COMM = 0
    ROBOT_STATE_ESTOPPED = 1
    ROBOT_STATE_NEEDS_RESET = 2
    ROBOT_STATE_RUNNING = 3

    # battery state
    BATTERY_STATE_NO_COMM = 0
    BATTERY_STATE_OK = 1
    BATTERY_STATE_LOW = 2
    BATTERY_STATE_FULL = 3
    BATTERY_STATE_FAULTED = 4

    # temperature state
    TEMPERATURE_STATE_NO_COMM = 0
    TEMPERATURE_STATE_OK = 1
    TEMPERATURE_STATE_LOW = 2
    TEMPERATURE_STATE_HIGH = 3

    # plugged in state
    PLUGGED_STATE_NO_COMM = 0
    PLUGGED_STATE_INACTIVE = 1
    PLUGGED_STATE_ACTIVE = 2

    # charging state
    CHARGING_STATE_NO_COMM = 0
    CHARGING_STATE_INACTIVE = 1
    CHARGING_STATE_ACTIVE = 2

    # driving state
    DRIVING_STATE_NO_COMM = 0
    DRIVING_STATE_OFF = 1
    DRIVING_STATE_ON = 2

    ########################
    # STATUS STATE STRINGS #
    ########################

    # robot state
    ROBOT_STATE_STR = {
        ROBOT_STATE_NO_COMM: "NO COMM",
        ROBOT_STATE_ESTOPPED: "ESTOPPED",
        ROBOT_STATE_NEEDS_RESET: "NEEDS RESET",
        ROBOT_STATE_RUNNING: "RUNNING",
    }

    # battery state
    BATTERY_STATE_STR = {
        BATTERY_STATE_NO_COMM: "NO COMM",
        BATTERY_STATE_OK: "OK",
        BATTERY_STATE_LOW: "LOW",
        BATTERY_STATE_FULL: "FULL",
        BATTERY_STATE_FAULTED: "FAULTED",
    }

    # temperature state
    TEMPERATURE_STATE_STR = {
        TEMPERATURE_STATE_NO_COMM: "NO COMM",
        TEMPERATURE_STATE_OK: "OK",
        TEMPERATURE_STATE_LOW: "LOW",
        TEMPERATURE_STATE_HIGH: "HIGH",
    }

    # plugged in state
    PLUGGED_STATE_STR = {
        PLUGGED_STATE_NO_COMM: "NO COMM",
        PLUGGED_STATE_INACTIVE: "INACTIVE",
        PLUGGED_STATE_ACTIVE: "ACTIVE",
    }

    # charging state
    CHARGING_STATE_STR = {
        CHARGING_STATE_NO_COMM: "NO COMM",
        CHARGING_STATE_INACTIVE: "INACTIVE",
        CHARGING_STATE_ACTIVE: "ACTIVE",
    }

    # driving state
    DRIVING_STATE_STR = {
        DRIVING_STATE_NO_COMM: "NO COMM",
        DRIVING_STATE_OFF: "OFF",
        DRIVING_STATE_ON: "ON",
    }

    #################
    # CLASS MEMBERS #
    #################

    def __init__(self):
        """Constructor for Status State."""

        # initialize everything to no comms
        self.robot_state = self.ROBOT_STATE_NO_COMM
        self.battery_state = self.BATTERY_STATE_NO_COMM
        self.temperature_state = self.TEMPERATURE_STATE_NO_COMM
        self.plugged_in_state = self.PLUGGED_STATE_NO_COMM
        self.charging_state = self.CHARGING_STATE_NO_COMM
        self.driving_state = self.DRIVING_STATE_NO_COMM
        # set all battery info to NaN
        self.battery_percent = math.nan
        self.battery_voltage = math.nan
        self.battery_amps = math.nan
        self.battery_temp = math.nan

    def __str__(self):
        """String representation of Status State."""

        serialized_msg = f"Robot state: {self.ROBOT_STATE_STR[self.robot_state]}\n"
        serialized_msg += f"Battery state: {self.BATTERY_STATE_STR[self.battery_state]}\n"
        serialized_msg += f"Battery percent: {self.battery_percent}\n"
        serialized_msg += f"Battery volts: {self.battery_voltage}\n"
        serialized_msg += f"Battery amps: {self.battery_amps}\n"
        serialized_msg += f"Temperature state: {self.TEMPERATURE_STATE_STR[self.temperature_state]}\n"
        serialized_msg += f"Battery temp: {self.battery_temp}\n"
        serialized_msg += f"Plugged in state: {self.PLUGGED_STATE_STR[self.plugged_in_state]}\n"
        serialized_msg += f"Charging state: {self.CHARGING_STATE_STR[self.charging_state]}\n"
        serialized_msg += f"Driving state: {self.DRIVING_STATE_STR[self.driving_state]}\n"

        return serialized_msg
