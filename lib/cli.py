
import argparse


def parseCli():
    parser = argparse.ArgumentParser(
        description='Open a graphical interface in order to send a file to a Masso device.'
    )

    parser.add_argument('-i', '--ip',
        help='The pre-selected ip address of the device')
    parser.add_argument('-f', '--file', default='',
        help='The pre-selected file to send')

    return parser.parse_args()

