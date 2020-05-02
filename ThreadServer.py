# !/usr/bin/env python3

import socket
import sys
import threading
import random
import os
import time
buffer_size = 1024

'''HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
buffer_size = 1024'''
##Metodos Juego##
def crea_tablero(fil, col, val):
    '''Crea matriz con filas y columnas y valor que le pasemos'''
    tablero = []
    for i in range(fil):
        tablero.append([])
        for j in range(col):
            tablero[i].append(val)
    return tablero

def muestra_tablero(tablero):
    '''Muestra en filas y columnas la matriz que la pasemos'''
    print("")
    i = 1
    for fila in tablero:
        print(i, end=" ")
        for elem in fila:
            print(elem, end=" ")
        print("*")
        i = i + 1

    if i < 11:
        print("  1 2 3 4 5 6 7 8 9")
    else:
        print("   1 2 3 4 5 6 7 8 910111213141516")

def coloca_minas(tablero, minas, fil, col, Client_conn):
    '''Coloca en el tablero que le pasemos el numero de minas que le pasemos'''
    minas_ocultas = []
    lista_mina = []
    numero = 0
    while numero < minas:
        y = random.randint(0, fil - 1)
        x = random.randint(0, col - 1)
        if tablero[y][x] != 9:
            tablero[y][x] = 9
            y = str(y)
            bytesToSend = str.encode(y)
            Client_conn.sendall(bytesToSend)
            x = str(x)
            bytesToSend = str.encode(x)
            Client_conn.sendall(bytesToSend)
            numero += 1
            minas_ocultas.append((y, x))
            lista_mina.append(x)
            lista_mina.append(y)
            Client_conn.recv(buffer_size)
    return tablero, minas_ocultas, lista_mina

def coloca_pistas(tablero, fil, col):
    for y in range(fil):
        for x in range(col):
            if tablero[y][x] == 9:
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if 0 <= y + i <= fil - 1 and 0 <= x + j <= col - 1:
                            if tablero[y + i][x + j] != 9:
                                tablero[y + i][x + j] += 1
    return tablero

def rellenado(oculto, visible, y, x, fil, col, val):
    '''Recorre todas las casilla vecinas, y comprueba si son ceros,
    si lo son los descubre y las recorre las vecinas en busca de pistas, que tambien descubre'''
    ceros = [(y, x)]
    while len(ceros) > 0:
        y, x = ceros.pop()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if 0 <= y + i <= fil - 1 and 0 <= x + j <= col - 1:
                    if visible[y + i][x + j] == val and oculto[y + i][x + j] == 0:
                        visible[y + i][x + j] = 0
                        if (y + i, x + j) not in ceros:
                            ceros.append((y + i, x + j))
                    else:
                        visible[y + i][x + j] = oculto[y + i][x + j]
    return visible

def tablero_completo(tablero, fil, col, val, min):
    '''Comprueba si el tablero no tiene ninguna casilla con el valor visible inicial'''
    i = 0
    for y in range(fil):
        for x in range(col):
            if tablero[y][x] == val:
                '''return False'''
                i = i + 1
    if i == min:
        return True

    return False

def reemplaza_ceros(tablero, col, fil):
    for i in range(fil):
        for j in range(col):
            if tablero[i][j] == 0:
                tablero[i][j] = " "
    return tablero
##Metodos Juego##

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            Client_conn, Client_addr = socketTcp.accept()
            print("Conectado a", Client_addr)
            gestion_conexiones(listaConexiones, Client_conn)
            thread_read = threading.Thread(target=mecanica_game, args=[Client_conn, listaConexiones])
            thread_read.start()
    except Exception as e:
        print(e)

def gestion_conexiones(listaconexiones, conn):
    listaconexiones.append(conn)
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    '''print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())'''
    print("conexiones: ", len(listaconexiones))
    '''print(listaconexiones)'''

def mecanica_game(Client_conn, listaconexiones):
    try:
        jugando = True
        cur_thread = threading.current_thread()
        while jugando:
            print("Esperando a recibir datos... ")
            if len(listaConexiones) == 1:
                Client_conn.sendall(b"1")
                lev = Client_conn.recv(buffer_size)
            else:
                Client_conn.sendall(b"2")
                Client_conn.recv(buffer_size)
                bytesToSend = str.encode(lev)
                Client_conn.sendall(bytesToSend)

            lev = int(lev)
            if lev == 1:
                columnas = 9
                filas = 9
                minas = 10
            if lev == 2:
                columnas = 16
                filas = 16
                minas = 40

            visible = crea_tablero(filas, columnas, "-")
            oculto = crea_tablero(filas, columnas, 0)
            if len(listaConexiones) == 1:
                oculto, minas_ocultas, lista_mina = coloca_minas(oculto, minas, filas, columnas, Client_conn)
                oculto = coloca_pistas(oculto, filas, columnas)

            muestra_tablero(oculto)
            # Bucle principal#
            jugando = True
            while jugando:
                y = Client_conn.recv(buffer_size)
                y = int(y)
                x = Client_conn.recv(buffer_size)
                x = int(x)

                real = visible[y][x]

                mov = "m"
                if mov == "m":
                    if oculto[y][x] == 9:
                        visible[y][x] = "@"
                        Client_conn.sendall(b"d")
                        jugando = False

                    elif oculto[y][x] != 0:
                        visible[y][x] = oculto[y][x]
                        real = visible[y][x]
                        Client_conn.sendall(b"l")

                    elif oculto[y][x] == 0:
                        visible[y][x] = 0
                        visible = rellenado(oculto, visible, y, x, filas, columnas, "-")
                        visible = reemplaza_ceros(visible, filas, columnas)
                        real = visible[y][x]
                        Client_conn.sendall(b"s")

                x = y = 0
                muestra_tablero(oculto)
                ganas = False

                if tablero_completo(visible, filas, columnas, "-", minas):
                    ganas = True
                    Client_conn.sendall(b"o")
                    jugando = False
                else:
                    Client_conn.sendall(b"e")

            if not ganas:
                print("******Has Perdido******")
                jugando = False
            else:
                print("******Has Ganado******")

    except Exception as e:
        print(e)
    finally:
        Client_conn.close()

listaConexiones = []
host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)