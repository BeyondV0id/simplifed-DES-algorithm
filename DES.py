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

# --- Helper Functions ---

def int_to_bits(value, size):
    """Convert integer to list of bits."""
    bits = []
    for i in reversed(range(size)):
        bits.append((value >> i) & 1)
    return bits

def bits_to_int(bits):
    """Convert list of bits to integer."""
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value


def perm(input_bits, perm_table):
    """Permute input array according to table."""
    output = [0] * len(perm_table)
    for i in range(len(perm_table)):
        # Tables are 1-based, arrays are 0-based
        index = perm_table[i] - 1
        output[i] = input_bits[index]
    return output

def ip(input_bits):
    """Perform the initial permutation on data."""
    return perm(input_bits, IPtable)

def fp(input_bits):
    """Perform the final permutation on data."""
    return perm(input_bits, FPtable)

def swapNibbles(input_bits):
    """Swap the two nibbles (4-bit halves) of data."""
    # Takes [0,1,2,3, 4,5,6,7] and returns [4,5,6,7, 0,1,2,3]
    return input_bits[4:] + input_bits[:4]

def keyGen(key_bits):
    """Generate the two required subkeys."""
    
    def leftShift(bits):
        """Perform a circular left shift on 5-bit halves."""
        # Split into left (first 5) and right (last 5)
        left = bits[:5]
        right = bits[5:]
        
        # Shift left side: [1,2,3,4,0]
        shifted_left = left[1:] + [left[0]]
        # Shift right side
        shifted_right = right[1:] + [right[0]]
        
        return shifted_left + shifted_right

    # 1. Apply P10
    temp_key = perm(key_bits, P10table)
    shifted_once = leftShift(temp_key)
    subKey1 = perm(shifted_once, P8table)
    shifted_twice = leftShift(leftShift(shifted_once))
    subKey2 = perm(shifted_twice, P8table)
    
    return subKey1, subKey2

def fk(subKey, inputData):
    """Apply Feistel function on data with given subkey."""
    
    def F(sKey, right_nibble):
        # 1. Expansion Permutation (4 bits -> 8 bits)
        expanded = perm(right_nibble, EPtable)
        
        # 2. XOR with Subkey
        xor_result = []
        for i in range(8):
            xor_result.append(expanded[i] ^ sKey[i])
            
        # 3. S-Box Substitution
        # S0: Uses first 4 bits
        row0 = xor_result[0] * 2 + xor_result[3] # Bits 1 & 4
        col0 = xor_result[1] * 2 + xor_result[2] # Bits 2 & 3
        val0 = S0table[row0][col0]
        
        # S1: Uses last 4 bits
        row1 = xor_result[4] * 2 + xor_result[7]
        col1 = xor_result[5] * 2 + xor_result[6]
        val1 = S1table[row1][col1]
        
        # Convert S-Box integer results to bits (2 bits each)
        # We use a mini helper or manual assignment here
        sbox_outputs = [
            (val0 >> 1) & 1, val0 & 1,  # S0 bits
            (val1 >> 1) & 1, val1 & 1   # S1 bits
        ]
        
        # 4. P4 Permutation
        return perm(sbox_outputs, P4table)

    # Split input into left and right nibbles
    leftNibble = inputData[:4]
    rightNibble = inputData[4:]
    
    # Calculate F function result
    f_result = F(subKey, rightNibble)
    
    # XOR Left Nibble with F result
    new_left = []
    for i in range(4):
        new_left.append(leftNibble[i] ^ f_result[i])
        
    # Combine: (Left ^ F(Right)) + Right
    return new_left + rightNibble

def encrypt(key_val, plaintext_val):
    """Encrypt plaintext with given key."""
    # Convert integers to bit arrays
    key_bits = int_to_bits(key_val, 10)
    plain_bits = int_to_bits(plaintext_val, 8)
    
    # Generate keys
    k1, k2 = keyGen(key_bits)
    
    # Run encryption steps
    # 1. IP
    data = ip(plain_bits)
    # 2. fk with K1
    data = fk(k1, data)
    # 3. Swap
    data = swapNibbles(data)
    # 4. fk with K2
    data = fk(k2, data)
    # 5. FP
    cipher_bits = fp(data)
    
    return bits_to_int(cipher_bits)

def decrypt(key_val, ciphertext_val):
    """Decrypt ciphertext with given key."""
    # Convert integers to bit arrays
    key_bits = int_to_bits(key_val, 10)
    cipher_bits = int_to_bits(ciphertext_val, 8)
    
    # Generate keys
    k1, k2 = keyGen(key_bits)
    
    # Run decryption steps (Reverse keys)
    # 1. IP
    data = ip(cipher_bits)
    # 2. fk with K2
    data = fk(k2, data)
    # 3. Swap
    data = swapNibbles(data)
    # 4. fk with K1
    data = fk(k1, data)
    # 5. FP
    plain_bits = fp(data)
    
    return bits_to_int(plain_bits)

# --- Main Execution ---

if __name__ == "__main__":
    plaintext = 0b10101010  # 170
    key = 0b1110001110      # 910
    
    print(f"Plaintext: {plaintext}")
    
    # Perform Encryption
    cipher = encrypt(key, plaintext)
    print(f"Cipher: {cipher}")
    
    # Convert Cipher to Binary String for display
    cipher_bits = int_to_bits(cipher, 8)
    cipher_binary_str = "".join(map(str, cipher_bits))
    print(f"Binary Cipher: {cipher_binary_str}")
