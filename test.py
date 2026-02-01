
# Tables for initial and final permutations (b1, b2, b3, ... b8)
IPtable = (2, 6, 3, 1, 4, 8, 5, 7)
FPtable = (4, 1, 3, 5, 7, 2, 8, 6)

KeyLength = 10
SubKeyLength = 8
DataLength = 8
FLength = 4

# Tables for initial and final permutations (b1, b2, b3, ... b8)
IPtable = (2, 6, 3, 1, 4, 8, 5, 7)
FPtable = (4, 1, 3, 5, 7, 2, 8, 6)

# Tables for subkey generation (k1, k2, k3, ... k10)
P10table = (3, 5, 2, 7, 4, 10, 1, 9, 8, 6)
P8table = (6, 3, 7, 4, 8, 5, 10, 9)

# Tables for the fk function
EPtable = (4, 1, 2, 3, 2, 3, 4, 1)
S0table = (1, 0, 3, 2, 3, 2, 1, 0, 0, 2, 1, 3, 3, 1, 3, 2)
S1table = (0, 1, 2, 3, 2, 0, 1, 3, 3, 0, 1, 0, 2, 1, 0, 3)
P4table = (2, 4, 3, 1)


IPtable = (2, 6, 3, 1, 4, 8, 5, 7)
def perm(inputbyte,permtable):
    outputbyte = 00000000
    for index,element in enumerate(input):
        if index >= element:
            """right shift the bit at element position to index position"""
            outputbyte = outputbyte | (input & (128 >> (element-1))) >> (index - (element-1))
        else:
            outputbyte = outputbyte | (input & (128 >> (element-1)) << ((element-1)-index))
    return outputbyte

def ip(inputbyte):
    return perm(inputbyte,IPtable)

def fp(inputbyte):
    return perm(inputbyte,FPtable)

def swapNibbles(inputByte):
    return (inputByte << 4 | inputByte >> 4)

