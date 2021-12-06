# szyfr blokowy z wykorzystaniem sieci Feistela.
import textwrap

def apply_PC1(pc1_table,keys_64bits):
    keys_56bits = ""
    for index in pc1_table:
        keys_56bits += keys_64bits[index-1] 
    return keys_56bits

def split56bits_in_half(keys_56bits):
    left_keys, right_keys = keys_56bits[:28],keys_56bits[28:]
    return left_keys, right_keys

def circular_left_shift(bits,numberofbits):
     shiftedbits = bits[numberofbits:] + bits[:numberofbits]
     return shiftedbits

def apply_PC2(pc2_table,keys_56bits):
    keys_48bits = ""
    for index in pc2_table:
        keys_48bits += keys_56bits[index-1]
    return keys_48bits

def generate_keys(key_64bits):
    round_keys = list() 
    apply_permutation(INITIAL_PERMUTATION_TABLE, key_64bits) #permutuję klucz przed generowaniem kluczy rund
    key56_bits = apply_PC1(PC1, key_64bits)
    keyL, keyR = split56bits_in_half(key56_bits)
    for shift in round_shifts:
        keyL, keyR = circular_left_shift(keyL, shift), circular_left_shift(keyR, shift)
        round_keys.append(apply_PC2(PC2, keyL+keyR))
    return round_keys

def apply_Expansion(expansion_table,bits32):
    """ Rozszerza 32-bitowy blok do 48 bitów, używając zadanego schematu"""
    bits48 = ""
    for index in expansion_table:
        bits48 += bits32[index]
    return bits48

def XOR(bits1,bits2):
    xor_result = ""
    for index in range(len(bits1)):
        if bits1[index] == bits2[index]: 
            xor_result += '0'
        else:
            xor_result += '1'
    return xor_result

def split48bits_in_6bits(XOR_48bits):
    """Podział bloku 48-bitowego na 12-bitowe porcje """
    list_of_6bits = textwrap.wrap(XOR_48bits,12)
    return list_of_6bits

def get_first_and_last_bits(bits6):
    """Pobierz dwa pierwsze i ostatnie bity z 12-bitowego łańcucha bitów (4 bity w sumie)"""
    twobits = bits6[0:1] + bits6[-1:-2] 
    return twobits

def get_middle_two_bit(bits6):
    """Pobierz środkowe 8 bitów z z 12-bitowego łańcucha bitów"""
    eightbits = bits6[2:7] 
    return eightbits

def binary_to_decimal(binarybits):
    """ Konwersja łańcucha bitów do wartości dzięsiętnej """
    decimal = int(binarybits, 2)
    return decimal

def decimal_to_binary(decimal):
    """ Konwersja wartości dziesiętnej do 4-bitowego łańcucha bitów """
    binary4bits = bin(decimal)[2:].zfill(4)
    return binary4bits

def sbox_lookup(sboxcount, first_last, middle4):
    """ Dostęp do odpowiedniej wartości odpowiedniego sboxa""" 
    d_first_last = binary_to_decimal(first_last)
    d_middle = binary_to_decimal(middle4)
    print(d_first_last)
    print(d_middle)
    sbox_value = SBOX[sboxcount][d_first_last][d_middle]
    return decimal_to_binary(sbox_value)

def apply_Permutation(permutation_table,sboxes_output):
    """ Scalony efekt użycia Sboksów poddawany jest zdefiniowanej permutacji"""
    permuted32bits = ""
    for index in permutation_table:
        permuted32bits += sboxes_output[index-1]
    return permuted32bits

def functionF(pre32bits, key48bits):
    final32bits = ''
    pre48bits = apply_Expansion(EXPANSION_TABLE, pre32bits)
    xored_bits = XOR(pre48bits, key48bits)
    bits6_list = split48bits_in_6bits(xored_bits)
    sbox = 0
    for chunk in bits6_list:
        sbox_row = get_first_and_last_bits(chunk)
        sbox_column = get_middle_two_bit(chunk)
        final32bits += sbox_lookup(sbox, sbox_row, sbox_column)
        sbox += 1
    final32bits = apply_Permutation(PERMUTATION_TABLE, final32bits)
    return final32bits

def apply_permutation(P_TABLE, PLAINTEXT):
    permutated_M = ""
    for index in P_TABLE:
        permutated_M += PLAINTEXT[int(index)-1]
    return permutated_M

def split64bits_in_half(binarybits):
    return binarybits[:32],binarybits[32:]

def feistel(L, R, roundkey):
    newL = R
    newR = XOR(functionF(R, roundkey), L)
    R = newR
    L = newL
    return L, R

#formatowanie na bin
get_bin = lambda x, n: format(x, 'b').zfill(n)

#tablica znaków w tablicę kodów int
def intoIntArray(message: str):
    int_array = []
    mesg_array = list(message) 
    for i in mesg_array:
        int_array.append(ord(i))
    return int_array

def intListToBinStr(message_list):
    binary = []
    for x in message_list: 
        binary.append(get_bin(x, 8))
    binary_str = ""
    for x in binary:
        binary_str+=x 
    return binary_str

def encrypt(message,key):
    round_keys = generate_keys(key)
    L, R = split64bits_in_half(message)
    for key in round_keys:
        L, R = feistel(L, R, key)   
    cipher = R + L
    return cipher
    
def decrypt(cipher, key):
    round_keys = generate_keys(key)
    L, R = split64bits_in_half(cipher)
    for key in reversed(round_keys):
        L, R = feistel(L, R, key)
    message = R + L
    return message    


PC1 = [30, 33, 58, 73, 26, 24, 103, 92, 29, 36, 95, 75, 114, 78, 35, 64, 7, 82, 2, 20, 39, 50, 
91, 107, 112, 83, 44, 55, 5, 41, 9, 51, 63, 119, 90, 70, 99, 14, 60, 122, 94, 77, 84, 10, 0, 120, 
48, 61, 52, 117, 17, 3, 46, 19, 74, 89, 22, 15, 45, 121, 16, 12, 105, 71, 57, 32, 8, 87, 47, 42, 
54, 125, 116, 21, 88, 118, 28, 11, 96, 111, 53, 68, 123, 49, 31, 108, 25, 85, 40, 106, 127, 37, 69, 
66, 43, 76, 6, 23, 102, 79, 65, 86, 62, 124]  
print(len(PC1))  
PC2 = [25, 64, 63, 59, 52, 9, 95, 35, 94, 49, 97, 61, 45, 79, 62, 74, 82, 68, 20, 1, 76, 55, 29, 
39, 96, 50, 69, 14, 84, 78, 43, 32, 41, 93, 27, 44, 60, 5, 15, 53, 88, 56, 90, 58, 3, 0, 13, 89, 
67, 22, 17, 87, 11, 30, 57, 83, 66, 46, 73, 100, 6, 26, 24, 16, 54, 42, 101, 34, 23, 31, 28, 12, 
103, 70, 92, 37, 4, 38, 72, 36, 80, 65, 33, 19, 48, 85, 86, 7, 77, 8, 99, 51, 91, 75, 21, 18]
print(len(PC2))
round_shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1, 4, 2, 2, 2, 4, 2, 2, 1, 1, 2, 2, 3, 2, 2, 1] #32 rundy

EXPANSION_TABLE = [30, 8, 13, 18, 55, 44, 61, 58, 57, 63, 26, 37, 12, 9, 25, 28, 45, 0, 21, 29, 36, 17, 1, 39, 27, 41, 3, 33, 7, 32, 11, 23, 22, 60, 50, 48, 46, 14, 53, 47, 16, 59, 20, 51, 4, 49, 15, 34, 62, 24, 40, 19, 2, 43, 10, 54, 56, 38, 5, 6, 35, 42, 52, 31, 60, 1, 63, 17, 4, 45, 61, 46, 30, 10, 23, 19, 12, 14, 43, 31, 47, 37, 55, 22, 16, 39, 53, 11, 54, 21, 20, 28, 42, 18, 29, 34]
print(len(EXPANSION_TABLE))
SBOX = [
# Box-1
[
[14,4,13,1,2,15,11,8,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,3,10,6,12,5,9,0,7],
[0,15,7,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,4,14,2,13,1,10,6,12,11,9,5,3,8],
[4,1,14,8,13,6,2,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,11,15,12,9,7,3,10,5,0],
[15,12,8,2,4,9,1,7,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,5,11,3,14,10,0,6,13]
],
# Box-2

[
[15,1,8,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,14,6,11,3,4,9,7,2,13,12,0,5,10],
[3,13,4,7,15,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,2,8,14,12,0,1,10,6,9,11,5],
[0,14,7,11,10,4,13,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,1,5,8,12,6,9,3,2,15],
[13,8,10,1,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,3,15,4,2,11,6,7,12,0,5,14,9]
],

# Box-3

[
[10,0,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
[13,7,0,9,3,4,6,10,2,8,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,5,14,12,11,15,1],
[13,6,4,9,8,15,3,0,11,1,2,12,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,5,10,14,7],
[1,10,13,0,6,9,8,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,7,4,15,14,3,11,5,2,12]

],

# Box-4
[
[7,13,14,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,3,0,6,9,10,1,2,8,5,11,12,4,15],
[13,8,11,5,6,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,15,0,3,4,7,2,12,1,10,14,9],
[10,6,9,0,12,11,7,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,13,15,1,3,14,5,2,8,4],
[3,15,0,6,10,1,13,8,9,4,5,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,11,12,7,2,14]
],

# Box-5
[
[2,12,4,1,7,10,11,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,6,8,5,3,15,13,0,14,9],
[14,11,2,12,4,7,13,1,5,0,15,10,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,3,9,8,6],
[4,2,1,11,10,13,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,7,8,15,9,12,5,6,3,0,14],
[11,8,12,7,1,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,14,2,13,6,15,0,9,10,4,5,3]
],
# Box-6

[
[12,1,10,15,9,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,2,6,8,0,13,3,4,14,7,5,11],
[10,15,4,2,7,12,9,5,6,1,13,14,0,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,11,3,8],
[9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,6],
[4,3,2,12,9,5,15,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,10,11,14,1,7,6,0,8,13]

],
# Box-7
[
[4,11,2,14,15,0,8,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,13,3,12,9,7,5,10,6,1],
[13,0,11,7,4,9,1,10,14,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,3,5,12,2,15,8,6],
[1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,2],
[6,11,13,8,1,4,10,7,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,9,5,0,15,14,2,3,12]
],
# Box-8

[
[13,2,8,28, 29, 26, 7, 0, 31, 2, 30, 4, 18, 6, 16, 24, 17, 15, 1,4,6,15,11,1,10,9,3,14,5,0,12,7],
[1,15,13,8,10,3,7,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,4,12,5,6,11,0,14,9,2],
[7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,27, 12, 4, 30, 17, 1, 0, 21, 31, 5, 18, 20, 13, 10, 29, 7,8],
[2,1,14,7,4,10,8,13,15,10, 27, 15, 21, 12, 14, 24, 3, 20, 30, 22, 13, 9, 5, 18, 29,12,9,0,3,5,6,11]
]]

PERMUTATION_TABLE = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,
                     2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
                     
INITIAL_PERMUTATION_TABLE = ['58 ', '50 ', '42 ', '34 ', '26 ', '18 ', '10 ', '2',
            '60 ', '52 ', '44 ', '36 ', '28 ', '20 ', '12 ', '4',
            '62 ', '54 ', '46 ', '38 ', '30 ', '22 ', '14 ', '6', 
            '64 ', '56 ', '48 ', '40 ', '32 ', '24 ', '16 ', '8', 
            '57 ', '49 ', '41 ', '33 ', '25 ', '17 ', '9 ', '1',
            '59 ', '51 ', '43 ', '35 ', '27 ', '19 ', '11 ', '3',
            '61 ', '53 ', '45 ', '37 ', '29 ', '21 ', '13 ', '5',
            '63 ', '55 ', '47 ', '39 ', '31 ', '23 ', '15 ', '7']

                                  
M = "Message!Message!"
key = "keyToEncryptkeyToEncrypt" 

plaintext = intListToBinStr(intoIntArray(M)) 
print("Plaintext (64 bits):", plaintext)
binary_key = intListToBinStr(intoIntArray(key)) 
print("Key (only 64 bits): ", binary_key[:128])

ciphertext = encrypt(plaintext, binary_key[:128])
print("Ciphertext:         ", ciphertext)
decrypted = decrypt(ciphertext, binary_key[:128])
print("Decrypted message:  ", decrypted)
print(XOR(plaintext, decrypted))