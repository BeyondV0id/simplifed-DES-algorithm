
IPtable = (2, 6, 3, 1, 4, 8, 5, 7)
FPtable = (4, 1, 3, 5, 7, 2, 8, 6)

P10table = (3, 5, 2, 7, 4, 10, 1, 9, 8, 6)
P8table = (6, 3, 7, 4, 8, 5, 10, 9)

EPtable = (4, 1, 2, 3, 2, 3, 4, 1)
P4table = (2, 4, 3, 1)

S0table = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2]
]

S1table = [
    [0, 1, 2, 3],
    [2, 0, 1, 3],
    [3, 0, 1, 0],
    [2, 1, 0, 3]
]

def int_to_bits(array, n):
    bits = [];
    for i in reversed(range(n)):
        bits.append((array >> i) & 1)
    return bits

def bits_to_ints(bits):
    number = 0
    n = len(bits)
    for i in range(n):
        power = 2 ** i
        number += bits[i] * power
    return number

def perm(input_bits,perm_table):
    output = [0]*len(perm_table)
    for i in range(len(perm_table)):
        index = perm_table[i]-1
        output[i] = input_bits[index]

    return output

def ip(input_bits):
    return perm(input_bits,IPtable)

def fp(input_bits):
    return perm(input_bits,FPtable)

def swapNibbles(input_bits):
    #8 bit number [0,1,2,3 4,5,6,7] => [4,5,6,7 0,1,2,3]
    return input_bits[4:] + input_bits[:4]

# NOTE: S-DES Key Generation Algorithm
# Input: 10-bit key
# Output: Two 8-bit subkeys (K1 and K2)
# 1. Apply P10 permutation to the 10-bit key.
# 2. Split the result into two halves (5 bits each).
# 3. Perform a circular left shift by 1 on both halves.
# 4. Combine halves and apply P8 permutation to obtain K1.
# 5. Perform a circular left shift by 2 more positions on both halves.
# 6. Combine halves and apply P8 permutation again to obtain K2.
# Final result: Subkeys K1 and K2 are generated.

def keyGen(key_bits):

    def leftShift(key_bits):
        left = key_bits[:5]
        right = key_bits[5:]
        shifted_left = left[1:] + [left[0]]
        shifted_right = right[1:] + [right[0]]

        return shifted_left+shifted_right
    
    #p10 permutation
    permutated_key = perm(key_bits,P10table)
    shiftOne = leftShift(permutated_key)
    shiftTwo = leftShift(shiftOne)
    subkey1 = perm(shiftOne,P8table)
    subkey2 = perm(shiftTwo,P8table)

    return subkey1,subkey2


    
# NOTE: S-DES fk Function Algorithm
# Input:
#   - 8-bit data block
#   - 8-bit subkey (K1 or K2)
# Output:
#   - 8-bit transformed block
# 1. Split the 8-bit input into two halves:
#      Left (first 4 bits) and Right (last 4 bits).
# 2. Apply Expansion/Permutation (E/P) to the Right half,
#      expanding it from 4 bits to 8 bits.
# 3. XOR the expanded Right half with the subkey.
# 4. Split the result into two 4-bit halves.
# 5. Pass:
#      - left half through S-box S0,
#      - right half through S-box S1,
#    producing 2 bits from each.
# 6. Combine S-box outputs to form 4 bits.
# 7. Apply permutation P4 to these 4 bits.
# 8. XOR this result with the original Left half.
# 9. Combine:
#      (Left XOR result) + original Right half.
# Result: new 8-bit output block.


def fk(inputData,subKey):
    leftNibble = inputData[:4]
    rightNibble = inputData[4:]
    
    expandedRightNibble = perm(rightNibble,EPtable)

    def XOR(expandedRightNibble,subkey1):
        result = [0]*len(subkey1)
        for i in range(len(subkey1)):
            result[i] = expandedRightNibble[i]^subkey1[i]
        return result

    def SBox(xor_result):
        row0 = xor_result[0] * 2 + xor_result[3] # Bits 1 & 4
        col0 = xor_result[1] * 2 + xor_result[2] # Bits 2 & 3
        val1 = S0table[row0][col0]
        row1 = xor_result[4] * 2 + xor_result[7]
        col1 = xor_result[5] * 2 + xor_result[6]
        val2 = S1table[row1][col1]
        binaryVal1 = [(val1>>1)&1, val1&1]
        binaryVal2 = [(val2>>1)&1, val2&1]
        return binaryVal1+binaryVal2

    xor_result = XOR(expandedRightNibble,subKey)
    sbox_output = SBox(xor_result)
    p4Result = perm(sbox_output,P4table)
    left = []
    for i in range(4):
        left.append(leftNibble[i]^p4Result[i])

    return left+rightNibble

def encrypt(key_val, plaintext_val):
    key_bits = int_to_bits(key_val, 10)
    plain_bits = int_to_bits(plaintext_val, 8)

    k1, k2 = keyGen(key_bits)

    data = ip(plain_bits)
    data = fk(data, k1)
    data = swapNibbles(data)
    data = fk(data, k2)
    cipher_bits = fp(data)

    return bits_to_ints(cipher_bits)

def decrypt(key_val, ciphertext_val):
    key_bits = int_to_bits(key_val, 10)
    cipher_bits = int_to_bits(ciphertext_val, 8)

    k1, k2 = keyGen(key_bits)

    data = ip(cipher_bits)
    data = fk(data, k2)
    data = swapNibbles(data)
    data = fk(data, k1)
    plain_bits = fp(data)

    return bits_to_ints(plain_bits)


if __name__ == "__main__":

    plaintext = 0b10101010
    key = 0b1110001110

    print("Plaintext:", plaintext)

    cipher = encrypt(key, plaintext)
    print("Cipher:", cipher)

    decrypted = decrypt(key, cipher)
    print("Decrypted:", decrypted)



