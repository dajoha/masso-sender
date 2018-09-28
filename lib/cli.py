# -*- coding: UTF-8 -*-

import argparse


def parseCli():
    parser = argparse.ArgumentParser(
        description='Open a graphical interface in order to send a file to a Masso device.'
    )

    parser.add_argument('-i', '--ip',
        help='The pre-selected ip address of the device')
    parser.add_argument('-f', '--file', default='',
        help='The pre-selected file to send')
    parser.add_argument('-s', '--send', action='store_true',
        help="Don't open the interface, send directly the given file from the command line; "+
             "with this option, --ip and --file options are required.")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="Be verbose in the console, even if the gui is launched (only useful without "+
             "the --send option)")
    parser.add_argument('-q', '--quiet', action='store_true',
        help="Be quiet in the console (only useful with the --send option)")

    return parser.parse_args()

