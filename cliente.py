#!/usr/bin/env python3
import socket
import random
import os

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
buffer_size = 2048
##Metodos##
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

def coloca_minas(tablero, minas, fil, col, y, x):
    '''Coloca en el tablero que le pasemos el numero de minas que le pasemos'''
    minas_ocultas = []
    numero = 0
    if tablero[y][x] != 9:
        tablero[y][x] = 9
        TCPClientSocket.sendall(b"r")
        minas_ocultas.append((y, x))
    return tablero, minas_ocultas

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

def tablero_completo(tablero, fil, col, val):
    '''Comprueba si el tablero no tiene ninguna casilla con el valor visible inicial'''
    for y in range(fil):
        for x in range(col):
            if tablero[y][x] == val:
                return False
    return True

def presentacion():
    '''Pantalla Presentacion'''
    os.system("cls")
    print("********************")
    print("*    BUSCAMINAS    *")
    print("*     SORIANO      *")
    print("*                  *")
    print("*    1 = FACIL     *")
    print("*   2 = AVANZADO   *")
    print("********************")
    print()
    nivel = int(input("Introduce el nivel: "))
    print()
    return nivel

def reemplaza_ceros(tablero, col, fil):
    for i in range(fil):
        for j in range(col):
            if tablero[i][j] == 0:
                tablero[i][j] = " "
    return tablero
##Metodos##

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    pos = TCPClientSocket.recv(buffer_size)
    pos = int(pos)
    if pos == 1:
        print("Enviando mensaje...")
        lev = presentacion()
        lev = str(lev)
        bytesToSend = str.encode(lev)
        TCPClientSocket.sendall(bytesToSend)
        lev = int(lev)
    else:
        TCPClientSocket.sendall(b"1")
        lev = TCPClientSocket.recv(buffer_size)
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
    if pos == 1:
        num = 0
        while num < minas:
            y = TCPClientSocket.recv(buffer_size)
            y = int(y)

            x = TCPClientSocket.recv(buffer_size)
            x = int(x)
            oculto, minas_ocultas = coloca_minas(oculto, minas, filas, columnas, y, x)
            num += 1

    oculto = coloca_pistas(oculto, filas, columnas)
    os.system("cls")
    muestra_tablero(visible)

    # bucle principal#
    minas_marcadas = []
    jugando = True
    while jugando:
        # visible = menu(visible)
        y = int(input("Fila: "))
        x = int(input("Columna: "))
        y -= 1
        x -= 1
        real = visible[y][x]
        y = str(y)
        bytesToSend = str.encode(y)
        TCPClientSocket.sendall(bytesToSend)
        y = int(y)
        x = str(x)
        bytesToSend = str.encode(x)
        TCPClientSocket.sendall(bytesToSend)
        x = int(x)

        mov = "m"
        vali = TCPClientSocket.recv(buffer_size)
        vali = str(vali)

        if mov == "m":
            if vali == "b'd'":
                oculto[y][x] == 9
                visible[y][x] = "@"
                jugando = False

            elif vali == "b'l'":
                oculto[y][x] != 0
                visible[y][x] = oculto[y][x]
                real = visible[y][x]

            elif vali == "b's'":
                oculto[y][x] == 0
                visible[y][x] = 0
                visible = rellenado(oculto, visible, y, x, filas, columnas, "-")
                visible = reemplaza_ceros(visible, filas, columnas)
                real = visible[y][x]

        x = y = 0
        os.system("cls")
        muestra_tablero(visible)
        ganas = False
        vali = TCPClientSocket.recv(buffer_size)
        vali = str(vali)
        if vali == "b'o'":
            ganas = True
            jugando = False
        elif vali == "b'e'":
            ganas = False

    if not ganas:
        print("******Has Perdido******")

    else:
        print("******Has Ganado******")
