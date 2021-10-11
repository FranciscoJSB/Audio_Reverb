import numpy as np
import librosa as lb                            # librosa 0.8.1 ocupa version 1.20.0 de numpy
import os
import string
import subprocess
import soundfile as sf

from playsound import playsound
from fxpmath import Fxp

#Funcion principal, recibe los path del audio a procesar y el metodo de reverberacion que se desea usar

def MuestreoAudio(AudioPath, ProcesoPath):

    path = AudioPath                                #path del audio
    path = os.fspath(path)                          #retorna la representacion del path como file system
    y, sr = lb.load(path, sr=44100)                 #carga el audio a 44KHz
    i = 0      
    hexaArray = []                                  #array vacio de hexadecimales

    while i < 20:
    #while i < len(y):
        x = Fxp(y[i], True, 16, 8)                  #paso de fraccion a binario
        hexa = x.hex()                              #paso de binario a hexadecimal
        hexaArray.append(hexa)                      #array de valores hexadecimales
        i=i+1

    textFile = open('MuestreoHexaWav2.txt', 'w')    #se crea el archivo .txt en la carpeta de /home
    for i in hexaArray:                             #se revisa el array
        textFile.write(i.replace('0x','')+" ")      #se escriben los valores del array en el archivo de texto sin 0x
    textFile.close()

    file = open("hello_world.txt","wt")
    subprocess.run("/home/francisco/Desktop/HelloWorld",stdout=file)  # se llama el proceso para ejecutar el programa en ensamblador

    buffer = readFileIntoBuffer("MuestreoHexaWav.txt") #buffer toma el archivo de texto generado de ensamblador
    hexBufferToAudio(buffer)                        #se ejecuta el convertidor del archivo de ensamblador a decimal

# Adds trailing zeros
def twosComp(value):

    result = []  # Stores result as a list

    for digit in value:  # Ones complement, switches ones to zeroes and viceversa

        if digit == "0":
            result.append("1")
        else:
            result.append("0")

    # Plus 1
    # Looks for a zero to assign carried bit
    carry = result[-1] == "1"
    if not carry:
        result[-1] = "1"
    carryInd = -1
    while carry:
        if result[carryInd] == "1":
            result[carryInd] = "0"
            carryInd -= 1
        else:
            carry = False
            result[carryInd] = "1"

    return "".join(result)


# Function that adds trailing zeros to a string
def addTrailing(value, number):

    for _ in range(number):
        value += "0"

    return value

# Adds zeros to the right and left of the number when needed
def treatNum(value):

    size = len(value)

    if isNeg(value):
        # If it is a negative number, the representation already has 8 bits at the front
        # Only trailing is needed
        # E.g. 1 0000000 101
        filled_value = addTrailing(value, 16 - size)
        return filled_value

    else:
        filled_value = value.zfill(8 + size)

        filled_value = addTrailing(filled_value, 8 - size)

        return filled_value

# Checks if the fixed point value is negative
def isNeg(value):

    if value == "0":
        return False

    zeroCount = 0

    found = False

    index = 1

    if value[0] != "1":
        return False

    while zeroCount < 7 and not found and index < len(value):
        if value[index] == "0":
            zeroCount += 1

        else:
            found = True

        index += 1

    if not found and zeroCount < 7:
        return False

    if found:
        return False

    return True

# Converts fixed point to dec
def pfToDec(value):

    if len(value) >= 16:
        sign = value[0]

        int_part = value[1:8]

        fract_part = value[8:16]

        if int(sign):  # If the value is negative, calculate twos complement
            int_part = twosComp(int_part)
            fract_part = twosComp(fract_part)

        result = fractToDec(fract_part)

        if int(sign):
            result *= -1

        return result

    treated_value = treatNum(value)

    sign = treated_value[0]

    int_part = treated_value[1:8]

    fract_part = treated_value[8:16]

    if int(sign):
        int_part = twosComp(int_part)
        fract_part = twosComp(fract_part)

    result = fractToDec(fract_part)

    if int(sign):
        result *= -1

    return result

# Fraction part to dec
def fractToDec(value):

    power = -1
    result = 0

    for digit in value:

        result += int(digit) * 2 ** power
        power -= 1

    return result

# Converts hex to fixed point
def hexToPf(value):
    # Hex has to have 4 digits
    treated = value.lower().zfill(4)  # Fills missing digits in hex
    result = ""
    hex = "0123456789abcdef"
    bin = [
        "0000",
        "0001",
        "0010",
        "0011",
        "0100",
        "0101",
        "0110",
        "0111",
        "1000",
        "1001",
        "1010",
        "1011",
        "1100",
        "1101",
        "1110",
        "1111",
    ]
    for i in treated:
        for j in range(len(hex)):
            if i == hex[j]:
                result += bin[j]
    return result

# Reads processed file into a buffer
def readFileIntoBuffer(name):
    file = open(name)

    line = file.read().replace("\n", " ")
    buffer = line.split()
    file.close()

    return buffer

# Converts audio buffer to an audio file
def hexBufferToAudio(buffer):

    audio_buffer = []

    for hex in buffer:
        pf = hexToPf(hex)  # Converts hex buffer value to fixed point
        dec = pfToDec(pf)  # Converts fixed point buffer value to dec

        audio_buffer.append(dec)  # Adds converted value to the final audio buffer

    sf.write(
        "Audio.wav", audio_buffer, 44100, "PCM_24"
    )  # Writes buffer into an audio file

    return playsound('/home/francisco/Audio.wav')

####################################################################################################################################

AudioPath = '/home/francisco/Downloads/10second.wav'

ProcesoPath = "/home/francisco/Desktop/HelloWorld"

MuestreoAudio(AudioPath, ProcesoPath)
#####################################################################################################################################
