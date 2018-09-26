
def sendFile(ip, path):
    print "SEND!!"
    return

    UDP_IP = ip
    UDP_PORT = 65535
    nom_fichier= path
    print(ip)

    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("chemin : ", path)


    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind(('0.0.0.0', 11000))
    sock.setblocking(0)


    fichier=open(nom_fichier, "rb").read()
    Longueur = len(fichier)
    nb_bloc= Longueur/1460 +1
    Longueur_hex=[hex(int(Longueur) >> i & 0xff) for i in (24,16,8,0)]
    #Longueur_hex=bytes(Longueur)
    array_Longueur = []
    #entete = []
    print("Nom du fichier : ",nom_fichier)
    print("longueur du fichier : ",Longueur)
    print("hexa : ", Longueur_hex[::-1])
    print("hexa longueur : ", len(Longueur_hex))
    print("Nombre de blocs : ",nb_bloc)

    Longueur_bytes=bytearray([int(x,0) for x in Longueur_hex[::-1]])
    Fichier_byte = bytearray()
    Fichier_byte.extend(os.path.basename(nom_fichier))
    Byte_blank=(bytearray([0x00,0x00,0x00,0x00,0x00,0x00]))
    print("Longueur array : ", Longueur_bytes )
    entete_form=[0x01, 0x00, 0x09,0x09,0x11,0x35,0x00]
    #entete_form=entete_form+Longueur_bytes
    print("Entete form : ",entete_form)
    entete=bytearray(entete_form)+Longueur_bytes+Byte_blank+Fichier_byte+bytearray([0x00])

    #entete=entete+Longueur_hex
    sock.sendto(bytearray([0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), (UDP_IP, UDP_PORT))
    time.sleep(0.2)

    print("Entete : ",entete)
    sock.sendto(entete, (UDP_IP, UDP_PORT))
    #sock.sendto(bytearray([0x01, 0x00, 0x09, 0x09, 0x1f, 0x1f, 0x51, 0x51, 0x3f, 0x2b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x48, 0x48, 0x2e, 0x6e,0x63,0x00]), (UDP_IP, UDP_PORT))
    time.sleep(0.2)
    entete_fichier = [0x01, 0x00, 0x0a, 0x09, 0x2d, 0x1c, 0x7f]

    offset=0
    num_dec2=0
    # Envoi du fichier
    for i in range(0,nb_bloc) :
        fichier_cut = fichier[i*1460:1460*i+1460]
        num_dec=i-offset
        num2=format(num_dec2, '02x')
        num=format(num_dec, '02x')
        print(num)
        if num_dec >= int(0xff) :
            num_dec2=num_dec2+1
            offset=i
        sock.sendto(bytearray(entete_fichier)+bytearray.fromhex(str(num))+bytearray.fromhex(str(num2))+bytearray([0x00,0x00])+fichier_cut, (UDP_IP, UDP_PORT))
        time.sleep(0.15)
        data = sock.recv(2048)
        if data=="":
            time.sleep(1)
        else:
            #print(data)
            data=""

