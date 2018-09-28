# -*- coding: UTF-8 -*-

import os
import socket
import time

from exceptions import MassoException
import logger


#################################  CONSTANTS  ##################################


# The encoding to use to send filenames for example (TODO?):
ENCODING = 'utf-8'

# The client port (TODO?)
CLIENT_PORT = 11000

# The Masso device port:
MASSO_PORT = 65535

# The data block size to send to the Masso device:
BLOCKSIZE = 1460


# Data transmission error settings:

# Number of retries for calling 'MassoSocket.recv()' before throwing an exception:
NB_RECV_RETRIES = 16
# Time to wait before each call of 'MassoSocket.recv()', in seconds:
TIME_BEFORE_RECV_RETRY = 0.05


# For debug:
MASSO_DEBUG_EMUL = os.getenv('MASSO_DEBUG_EMUL', False)
if MASSO_DEBUG_EMUL:
    import random


##############################  UTILITY FUNCTIONS  #############################


def to_str(s, error_msg):
    """ Convert unicode strings to byte strings, keep byte strings as-is, and raise an error if the
        arg is not a string at all.
    """
    if isinstance(s, unicode):
        return s.encode(ENCODING)
    elif isinstance(s, str):
        return s
    else:
        error(error_msg)


def str2bytearray(s):
    """ Convert a string to a bytearray. """
    return bytearray([ ord(c) for c in s ])


def bytearray2human(l):
    """ Convert a bytearray to a human readable string (hexa codes). """
    hexs = [ "%0.2X" % c for c in l ]
    return ' '.join(hexs)


def bytearray2chars(l):
    """ Convert a bytearray to a human readable string (readable chars or spaces). """
    s = ''
    for asc in l:
        c = (asc < 32) and ' ' or chr(asc)
        s += c + '  '
    return s


def get64bits(n):
    """ Return a list of 4 bytes (<256) representing the given number as a 4-byte suite
        (little-endian)
    """
    return [ n >> i & 0xff for i in (0,8,16,24) ]


def zeroes(n):
    """ Return a list of 'n' 0 values. """
    return [0] * n


def dumpBytearrayData(title, data):
    """ Dump a short bytearray data block. If the display is too long for a console line, the
        display will be scrapped.
    """
    print "{}: | {}".format(title, bytearray2human(data))
    print "{}  | {}".format(' '*len(title), bytearray2chars(data))


def dumpStrData(title, string):
    """ Dump a short string data block. If the display is too long for a console line, the
        display will be scrapped.
    """
    dumpBytearrayData(title, str2bytearray(string))


def getBytearray(data):
    """ Return a bytearray conversion of the given data:
         - if the data is a list or a string, convert it to a bytearray;
         - if the data is an integer, convert it to a single-element bytearray;
         - if the data is already a bytearray, keep it as-is;
         - otherwise, raise an error
    """
    if isinstance(data, list) or isinstance(data, str):
        return bytearray(data)
    elif isinstance(data, int):
        return bytearray([ data ])
    elif isinstance(data, bytearray):
        return data
    else:
        raise MassoException("Frame: data type not handled ({})"
            .format(type(data))
        )


def logProgress(masso_socket, N, nb_blocks):
    """ Display a progress message. """

    percent = N * 100 / nb_blocks
    msg = "[{}%] Data block {}/{} (recv retries: avg:{}, max:{}, allowed:{})".format(
        percent,
        N, nb_blocks,
        masso_socket.averageRecvRetries, masso_socket.maxRecvFrameRetries,
        NB_RECV_RETRIES
    )

    logger.erase()
    logger.log(msg)



##############################  CLASS DEFINITIONS  #############################


class MassoSocket:
    """ Represent a python socket to connect to a Masso device. """

    def __init__(self, ip=None, inputFile=None):
        """ Constructor.
            'ip' is the Masso device's ip;
            'inputFile' is the file path to send to the Masso device.
        """

        if ip == None or inputFile == None:
            self.error("Missing constructor parameter")

        self.ip = ip
        self.inputFile = inputFile

        self.sock = socket.socket(
            socket.AF_INET,   # Internet
            socket.SOCK_DGRAM # UDP
        )
        self.sock.bind(('0.0.0.0', CLIENT_PORT))
        self.sock.setblocking(0)

        self.destAddress = (self.ip, MASSO_PORT)

        # Initialize some debug variables:

        # How many times the recv() method fails:
        self.recvFailCount = 0
        # How many retries for calling `recv()` where needed in the last `sendFrame()` call:
        self.lastRecvFrameRetries = 0
        # Maximum `recv()` retries:
        self.maxRecvFrameRetries = 0
        # Average `recv()` retries per call of `sendFrame()`:
        self.averageRecvRetries = 0
        # How many retries for calling `recv()` where needed for all the `sendFrame()` calls:
        self.nbRecvFrameRetries = 0
        # How many times `sendFrame()` was called:
        self.nbSendFrameCalls = 0


    def sendPing(self):
        """ High-level frame handling: send a ping to the Masso device. """

        frame_header = [ 0x01, 0x00, 0x01 ]

        return self.sendFrame(frame_header, title="Ping")


    def sendFileTransferOrder(self, filename, data_length):
        """ High-level frame handling: send a file transfer order to the Masso device. """

        frame_header = [ 0x01, 0x00, 0x09, 0x09, 0x11, 0x35, 0x00 ]

        return self.sendFrame(
            frame_header,
            get64bits(data_length),
            zeroes(6),
            filename,
            0,
            title="File Transfer Order"
        )


    def sendDataBlock(self, n, data_block):
        """ High-level frame handling: send a file data block to the Masso device. """

        frame_header = [ 0x01, 0x00, 0x0a, 0x09, 0x2d, 0x1c, 0x7f ]

        return self.sendFrame(
            frame_header,
            get64bits(n),
            data_block,
            title="Data Block {}".format(n)
        )


    def sendFrame(self, *datas, **kwds):
        """ Send some data to the Masso device, in a higher level than 'send()':
            Each unnamed parameter (list|bytearray|string|integer) is appended to the frame data;
            A 'title' parameter can be passed in order to describe which kind of frame is being sent
            (can be useful for debugging)
        """

        self.nbSendFrameCalls += 1

        frame = Frame(*datas)
        self.send(frame)

        self.lastRecvFrameRetries = 0
        response = None
        for i in range(NB_RECV_RETRIES):
            try:
                time.sleep(TIME_BEFORE_RECV_RETRY)
                response = self.recv()
                break
            except Exception as e:
                self.lastRecvFrameRetries += 1
                pass

        self.updateRecvInfos()

        if response == None:
            msg = "No response from the device"
            if ('title' in kwds):
                msg += ' (frame: {})'.format(kwds['title'])
            self.error(msg)

        return response


    def send(self, data):
        """ Send some raw data to the Masso device.
            if 'data' is an instance of Frame, then use the frame data.
        """

        if isinstance(data, Frame):
            self.send(data.data)
        else:
            if MASSO_DEBUG_EMUL:
                pass
            else:
                self.sock.sendto(data, self.destAddress)


    def recv(self):
        """ Try to receive a pending frame. May throw an exception on fail. """

        try:
            if MASSO_DEBUG_EMUL:
                if random.randint(0, 100) < 50:
                    raise MassoException("fake exception")
                return "fake data"
            else:
                return self.sock.recv(2048)
        except Exception as e:
            self.recvFailCount += 1
            raise e


    def updateRecvInfos(self):
        """ Update debug informations about the number of retries for 'recv()'. """

        self.nbRecvFrameRetries += self.lastRecvFrameRetries
        self.averageRecvRetries = self.nbRecvFrameRetries / self.nbSendFrameCalls
        if self.lastRecvFrameRetries > self.maxRecvFrameRetries:
            self.maxRecvFrameRetries = self.lastRecvFrameRetries


    def error(self, msg):
        """ Throw an error relative to MassoSocket. """
        raise MassoException("MassoSocket: {}".format(msg))

# END OF CLASS 'MassoSocket'




class Frame:
    """ Represent a UDP frame to send to a Masso device. It's basically a bytearray with facilities
        to append elements to it (see function (getBytearray()).
    """

    def __init__(self, *datas):
        """ Constructor.
            Can take any number of arguments, each one being a data (list|bytearray|string|integer)
            to append.
        """
        self.set(*datas)

    def set(self, *datas):
        """ Set the data of the frame.
            Can take any number of arguments, each one being a data (list|bytearray|string|integer)
            to append.
        """
        self.data = bytearray()
        self.append(*datas)

    def append(self, *new_datas):
        """ Append datas to the data of the frame.
            Can take any number of arguments, each one being a data (list|bytearray|string|integer)
            to append.
        """
        for new_data in new_datas:
            self.data += getBytearray(new_data)

    def append64bits(self, num):
        """ Append a 4-bytes number. """
        self.append(get64bits(num))

# END OF CLASS 'Frame'




###############################  MAIN FUNCTIONS  ###############################


def sendFile(masso_ip, input_file):
    """ Send a file to a Masso device. """

    masso_ip = to_str(masso_ip, 'Bad IP value')

    print("Masso target: {}:{}".format(masso_ip, MASSO_PORT))


    # Create the MassoSocket instance:

    masso_sock = MassoSocket(masso_ip, input_file)


    # Retrieve the file data:

    input_file = to_str(input_file, 'Bad input file')
    filename = os.path.basename(input_file)

    input_data = open(input_file, "rb").read()

    data_length = len(input_data)
    nb_blocks = data_length / BLOCKSIZE + 1

    print("Filename: {} ({} bytes, {} data block{})".format(
        filename, data_length, nb_blocks, nb_blocks > 1 and 's' or ''
    ))


    # Send the file transfer order frame to the Masso device:

    response = masso_sock.sendFileTransferOrder(filename, data_length)


    # Send the file data to the Masso device:

    for N in range(nb_blocks) :
        data_block = input_data[N*BLOCKSIZE : (N+1)*BLOCKSIZE]
        response = masso_sock.sendDataBlock(N, data_block)
        logProgress(masso_sock, N, nb_blocks)

    logProgress(masso_sock, nb_blocks, nb_blocks)
    logger.newline()
    print "File transfered with success."

