#!/usr/bin/env python3

import argparse
import sys
import rclpy
from togo_status_handler.status_tui_backend_node import StatusTUIBackendNode
from togo_status_handler.status_tui_frontend import StatusTUIFrontend


def main(args=None):
    rclpy.init(args=args)

    # initialize parser and parse args
    parser = argparse.ArgumentParser(
        epilog="Note that if specifying program args and ros args, program args must come first"
    )
    parser.add_argument(
        "-n", "--no-display", action="store_true", help="Print status to terminal but do not start an Ncurses display"
    )
    parsed_args, unknown_args = parser.parse_known_args()

    # set display
    if parsed_args.no_display:
        display = None
    else:
        display = StatusTUIFrontend()

    # create status TUI node
    status_node = StatusTUIBackendNode(display)
    rclpy.spin(status_node)

    # destroy nodes
    status_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main(sys.argv)
