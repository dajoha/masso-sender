# encoding: UTF-8

import sys


reg = ''


def flush():
    sys.stdout.flush()

def write(msg):
    sys.stdout.write(msg)

def log(msg):
    """ Write a message without eol, which is erasable with 'erase()'. """
    global reg
    write(msg)
    reg += msg
    flush()

def erase():
    """ Erase a previously logged message, in the current line. """
    global reg
    write('\r')
    write(' ' * len(reg))
    write('\r')
    reg = ''
    flush()

def newline():
    """ Start a new line, and reset the old written message """
    global reg
    print
    reg = ''

