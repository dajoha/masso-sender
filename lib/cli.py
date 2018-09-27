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
        help="Send directly the given file from command line, don't open the interface")

    return parser.parse_args()

