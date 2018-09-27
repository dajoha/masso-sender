# -*- coding: UTF-8 -*-

import os
import socket
import time


def sendFile(ip, path):
    UDP_IP = ip.encode('utf-8')
    nom_fichier = path.encode('utf-8')
    UDP_PORT = 65535

    print("UDP target IP: {}".format(UDP_IP))
    print("UDP target port: {}".format(UDP_PORT))
    print("Input file : {}".format(nom_fichier))


    sock = socket.socket(
        socket.AF_INET,   # Internet
        socket.SOCK_DGRAM # UDP
    )
    sock.bind(('0.0.0.0', 11000))
    sock.setblocking(0)


    fichier = open(nom_fichier, "rb").read()
    Longueur = len(fichier)
    nb_bloc = Longueur/1460 + 1
    Longueur_hex = [hex(int(Longueur) >> i & 0xff) for i in (24,16,8,0)]
    array_Longueur = []

    print("Longueur du fichier : {}".format(Longueur))
    print("Hexa : {}".format(Longueur_hex[::-1]))
    print("Nombre de blocs : {}".format(nb_bloc))

    Longueur_bytes = bytearray([int(x,0) for x in Longueur_hex[::-1]])
    Fichier_byte = bytearray()
    Fichier_byte.extend(os.path.basename(nom_fichier))
    Byte_blank = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    print("Longueur array : {}".format(Longueur_bytes))
    entete_form = [0x01, 0x00, 0x09, 0x09, 0x11, 0x35, 0x00]
    #entete_form=entete_form+Longueur_bytes
    print("Entete form : {}".format(entete_form))
    entete = bytearray(entete_form) + Longueur_bytes + Byte_blank + Fichier_byte + bytearray([0x00])

    #entete=entete+Longueur_hex
    sock.sendto(bytearray([0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), (UDP_IP, UDP_PORT))
    time.sleep(0.2)

    print("Entete : {}".format(entete))
    sock.sendto(entete, (UDP_IP, UDP_PORT))

    time.sleep(0.2)
    entete_fichier = [0x01, 0x00, 0x0a, 0x09, 0x2d, 0x1c, 0x7f]

    offset = 0
    num_dec2 = 0

    # Envoi du fichier:
    for i in range(0,nb_bloc) :
        fichier_cut = fichier[i*1460 : 1460*i+1460]
        num_dec = i - offset
        num2 = format(num_dec2, '02x')
        num = format(num_dec, '02x')
        print(num)
        if num_dec >= int(0xff):
            num_dec2 = num_dec2 + 1
            offset = i
        sock.sendto(bytearray(entete_fichier)+bytearray.fromhex(str(num))+bytearray.fromhex(str(num2))+bytearray([0x00,0x00])+fichier_cut, (UDP_IP, UDP_PORT))
        time.sleep(0.15)
        data = sock.recv(2048)
        if data == "":
            time.sleep(1)
        else:
            #print(data)
            data = ""
