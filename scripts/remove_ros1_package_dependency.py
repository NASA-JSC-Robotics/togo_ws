#!/usr/bin/env python3

import argparse
import sys


def remove_ros1_package_dependency(file_path, find_str, repl_str):
    # read the file
    file = open(file_path)
    lines = file.readlines()
    file.close()

    # find line to be replaced
    new_lines = []
    for line in lines:
        if find_str in line:
            # check if replacement has already been made
            if repl_str in line:
                continue
            # replace text
            line = line.replace(find_str, repl_str)
        # add line to new lines
        new_lines.append(line)

    # write the file
    file = open(file_path, "w")
    for line in new_lines:
        file.write(line)
    file.close()

    return


def main():
    parser = argparse.ArgumentParser("Remove ROS1 Dependency")
    parser.add_argument("-p", "--path", help="Path to the package.xml file to be modified")

    # parse arguments
    parsed_args = parser.parse_args(sys.argv[1:])

    # set variables
    file_path = "package.xml"
    file_path = parsed_args.path + "/" + file_path
    ros1_depend = "<depend>fpsdk_ros1</depend>"
    commented_depend = "<!-- <depend>fpsdk_ros1</depend> -->"

    # find/replace dependency
    remove_ros1_package_dependency(file_path, ros1_depend, commented_depend)

    return


if __name__ == "__main__":
    main()
