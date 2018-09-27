# -*- coding: UTF-8 -*-

import os
import socket
import time

from lib.exceptions import MassoException


ENCODING = 'utf-8'

SRC_PORT = 11000
DEST_PORT = 65535
BLOCKSIZE = 1460


def to_str(s, error_msg):
    """ Convert unicode strings to strings, and raise an error if the arg is not as string. """
    if isinstance(s, unicode):
        return s.encode(ENCODING)
    elif isinstance(s, str):
        return s
    else:
        error(error_msg)


def str2list(s):
    return [ ord(c) for c in s ]


def list2human(l):
    hexs = [ "%0.2X" % c for c in l ]
    return ' '.join(hexs)


def list2chars(l):
    s = ''
    for asc in l:
        c = (asc < 32) and ' ' or chr(asc)
        s += c + '  '
    return s


def get64bits(n):
    return bytearray([ n >> i & 0xff for i in (0,8,16,24) ])


def zeroes(n):
    return bytearray([0]) * n


def dumpListData(title, data):
    print "{}: | {}".format(title, list2human(data))
    print "{}  | {}".format(' '*len(title), list2chars(data))


def dumpStrData(title, string):
    l = str2list(string)
    dumpListData(title, l)


def getBytearray(data):
    if isinstance(data, list) or isinstance(data, str):
        return bytearray(data)
    elif isinstance(data, int):
        return bytearray([ data ])
    elif isinstance(data, bytearray):
        return data
    else:
        raise MassoException("Trame: data type not handled ({})"
            .format(type(data))
        )




class MassoSocket:
    def __init__(self, ip=None, inputFile=None):
        if ip == None or inputFile == None:
            self.error("Missing constructor parameter")

        self.ip = ip
        self.inputFile = inputFile

        self.sock = socket.socket(
            socket.AF_INET,   # Internet
            socket.SOCK_DGRAM # UDP
        )
        self.sock.bind(('0.0.0.0', SRC_PORT))
        self.sock.setblocking(0)

        self.destAddress = (self.ip, DEST_PORT)

    def send(self, data):
        if isinstance(data, Trame):
            self.send(data.data)
        else:
            self.sock.sendto(data, self.destAddress)

    def sendTrame(self, *datas, **kwds):
        trame = Trame(*datas)
        self.send(trame)

        #  time.sleep(0.15)
        #  resp = self.recv()

        resp = None
        for i in range(16):
            try:
                time.sleep(0.05)
                resp = self.recv()
                break
            except Exception as e:
                pass

        if resp == None:
            msg = "No response from the device"
            if ('title' in kwds):
                msg += ' (trame: {})'.format(kwds['title'])
            self.error(msg)

        return resp

    def recv(self):
        return self.sock.recv(2048)

    def sendFileTransferOrder(self, filename, data_length):
        trame_header = [ 0x01, 0x00, 0x09, 0x09, 0x11, 0x35, 0x00 ]

        return self.sendTrame(          \
            trame_header,               \
            get64bits(data_length),     \
            zeroes(6),                  \
            filename,                   \
            0,                          \
            title="file transfer order" \
        )

    def sendDataBlock(self, n, data_block):
        trame_header = [ 0x01, 0x00, 0x0a, 0x09, 0x2d, 0x1c, 0x7f ]

        return self.sendTrame( \
            trame_header,      \
            get64bits(n),      \
            data_block,        \
            title="data block {}".format(n) \
        )

    def error(self, msg):
        raise MassoException("MassoSocket: {}".format(msg))



class Trame:
    def __init__(self, *datas):
        self.data = bytearray()
        for data in datas:
            self.data += getBytearray(data)

    def set(self, data):
        self.data = getBytearray(data)

    def append(self, *new_datas):
        for new_data in new_datas:
            self.data += getBytearray(new_data)

    def append64bits(self, num):
        self.append(get64bits(num))

    def zeroPad(self, size):
        self.append(zeroes(size))



def sendFile(ip, input_file):
    """ Send a file to a Masso device. """

    def error(msg):
        """ Raise an error """
        raise MassoException("sendFile(): {}".format(msg))

    DEST_IP = to_str(ip, 'Bad IP value')

    input_file = to_str(input_file, 'Bad input file')
    filename = os.path.basename(input_file)

    print("UDP target IP: {}".format(DEST_IP))
    print("UDP target port: {}".format(DEST_PORT))
    print("Input file : {}".format(input_file))


    masso_sock = MassoSocket(ip=DEST_IP, inputFile=input_file)


    #  masso_sock.send(bytearray([0x01, 0x00, 0x01]))

    #  time.sleep(0.15)

    #  data = masso_sock.recv()
    #  human_data = [ c.encode('hex') for c in data ]
    #  print human_data

    #  return



    #  masso_sock.send(bytearray([0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    #  time.sleep(0.2)



    inputData = open(input_file, "rb").read()

    dataLength = len(inputData)
    nbBlocks = dataLength / BLOCKSIZE + 1

    print("Longueur du fichier : {}".format(dataLength))
    print("Nombre de blocs : {}".format(nbBlocks))



    # TRAME ORDRE D'ENVOI DE FICHIER:

    response = masso_sock.sendFileTransferOrder(filename, dataLength)

    dumpStrData('RESPONSE', response)


    # ENVOI DU FICHIER:

    for N in range(nbBlocks) :
        data_block = inputData[N*BLOCKSIZE : (N+1)*BLOCKSIZE]

        response = masso_sock.sendDataBlock(N, data_block)

        if response == "":
            time.sleep(1)

