import math
import re
from bitstring import Bits

SYMTAB = {
    'A': 0,
    'X': 1,
    'L': 2,
    'B': 3,
    'S': 4,
    'T': 5,
    'F': 6,
    'PC':8,
    'SW':9,
}

OPTAB = {
    'STA':0x0C,
    'STB':0x1C, #
    'STX':0x10,
    'STL':0x14,
    'STCH':0x54,

    'LDA':0x00,
    'LDX':0x04, #
    'LDCH':0x50,
    'LDB':0x68,
    'LDT':0x74,

    'COMP':0x28,
    'COMPR':0xA0,

    'J':0x3C,
    'JEQ':0x30,
    'JLT':0x38,
    'JSUB':0x48,

    'CLEAR':0xB4,

    'TIXR':0xB8,

    'RSUB':0x4C,

    'TD':0xE0,
    'RD':0xD8,
    'WD':0xDC,
}

registers = [0]*10

starting_addr = "000000"
LOCCTR = 0
BASETABLE = []
WBTAB = {}
LITERALTABLE = {}
regex = r"[XC]'(\w+)'"


output_file = []
file = open('code test.txt', mode='r')

def get_hash(s):
    output_hash = ""
    temp = abs(hash(s))
    while len(output_hash)< 3 or any([ output_hash[-3:] == V for L, V in  LITERALTABLE.items()]):
        output_hash += chr(temp % 26 + 65)
        temp//=100
    return output_hash[-3:]

def decode(s):
    s = s.lstrip('\t').rstrip('\n')
    arr = s.split()
    if arr[0] == 'BASE':
        BASETABLE.append(arr[1])
        return ["", "", ""]

    if len(arr) == 2:
        if arr[0].lstrip("+") in OPTAB or arr[0] == '*':
            arr = [""] + arr
        else:
            arr = arr + [""]
    elif len(arr) == 1:
        arr = [""] + arr + [""]
    return arr

def WB_function(s):
    for item in WBTAB[s]:
        if len(output_file[item]) == 8:
            address = str(Bits(uint=SYMTAB[s], length=20)).lstrip('0x').upper()
            output_file[item][-5:] += "{:0>5x}".format(address)
        elif len(output_file[item]) == 5:
            disp = str(Bits(uint=disp, length=12)).lstrip('0x').upper()
            output_file[item][-3:] += "{:0>3x}".format(disp)
        else:
            pass

def str_flag(nixbpe):
    return str(Bits(uint=int("".join([str(i) for i in nixbpe[2:]]), 2), length=4)).lstrip('0x').upper()
#            withindex  , OP
def format_2(output_file, OPCODE=0, OPERAND=0):
    if OPCODE == 'CLEAR' or OPCODE == 'TIXR':
        output_file += "{:x}{:x}".format(SYMTAB[OPERAND], 0)
    else:
        output_file += "{:x}{:x}".format(SYMTAB[OPERAND.split(',')[0]],
                                             SYMTAB[OPERAND.split(',')[1]]).upper()
    print("format 2, object code: {}".format(output_file))
    return output_file

def format_3(output_file, nixbpe, OPERAND=0):

    if OPERAND[0] == '=':
        OPERAND = LITERALTABLE[OPERAND]

    if (nixbpe[0] * 2 + nixbpe[1]) != 1 or OPERAND.isalpha():
        if OPERAND.lstrip('=').replace("\'", "").isalpha():
            disp = SYMTAB[OPERAND] - (
                int(LOCCTR, 16) if nixbpe[0] * 2 + nixbpe[1] != 1 else 0)
        else:
            disp = int(OPERAND) - (int(LOCCTR, 16) if nixbpe[0] * 2 + nixbpe[1] != 1 else 0)

        if -2048 <= disp <= 2047:  # Pc relative
            nixbpe[3] = 0
            nixbpe[4] = 1
        else:  # Base relative?
            disp = SYMTAB[OPERAND] - BASETABLE[0]
            if 0 <= disp <= 4095:
                nixbpe[3] = 1
                nixbpe[4] = 0
            else:
                print("cannot jump a gap")
                print("disp: {}, SYMTAB {}, BASETABLE {}".format(disp, SYMTAB[OPERAND], BASETABLE[0]))
                exit(187)
    else:
        disp = int(OPERAND)

    if disp >= 0:
        disp = str(Bits(uint=disp, length=12)).lstrip('0x').upper()
    else:
        disp = str(Bits(int=disp, length=12)).lstrip('0x').upper()
    output_file += str_flag(nixbpe)
    output_file += "{:0>3}".format(disp)
    print("format 3/4, object code: {}".format(output_file))
    return output_file

def format_4(output_file, OPERAND=0):
    address = 0
    if OPERAND[0] == '=':
        address = SYMTAB[LITERALTABLE[OPERAND]]
    elif OPERAND.isalpha():
        address = SYMTAB[OPERAND]
    else:
        address = int(OPERAND)
    if address != 0:
        try:
            address = str(Bits(uint=address, length=20)).lstrip('0x').upper()
        except:
            print("cannot jump a gap")
            print("address: {}, SYMTAB {}, BASETABLE {}".format(address, SYMTAB[OPERAND], BASETABLE[0]))
            exit(187)
        output_file += "{:0>5}".format(address)
    else:
        output_file.replace(output_file[-5:], "{:0>5x}".format(address))
    return output_file

line = file.readline()
[LABEL, OPCODE, OPERAND] = decode(line)

if OPCODE == 'START':
    starting_addr = OPERAND
    LOCCTR = int(OPERAND, 16)
    output_file.append("H"+LABEL+'\t' + "{:0>6}".format(starting_addr))
else:
    LOCCTR = 0


for index, line in enumerate(file.readlines()):
    output_file.append("")
    nixbpe = [0] * 6

    # LOCCTR.upper() CURT PC!!!
    [LABEL, OPCODE, OPERAND] = decode(line)

    if LABEL == '' and OPCODE == '' and OPERAND == '':
        print("BASE Set: {}".format(SYMTAB[BASETABLE[-1]]))
        continue

    print("{:0>4x}".format(LOCCTR).upper(), end=" ")
    print("LABEL: {:<8}, OPCODE: {:<8}, OPERAND: {:<8}".format(LABEL, OPCODE, OPERAND))

    if LABEL == 'END':
        output_file[0] += "{:0>6x}".format(LOCCTR - int(starting_addr, 16))
        print("finish!!!")
        break

    if LABEL != "":
        if SYMTAB.get(LABEL, -1) == -1:
            print("duplicate symbol")
            exit(187)
        else:
            # TODO
            SYMTAB[LABEL] = LOCCTR


    if OPCODE == '*':
        LITERALTABLE[OPERAND] = get_hash(OPERAND.lstrip("=XC'").rstrip("'"))
        # TODO
        SYMTAB[LITERALTABLE[OPERAND]] = LOCCTR


        matches = re.search(regex, OPERAND.lstrip('='))
        if OPERAND.lstrip('=')[0] == 'X':
            LOCCTR += math.ceil(len(matches.groups()[0]) * 4 / 24)
        else:  # 'C'
            LOCCTR += len(matches.groups()[0])
        print("auto LITERALT create address: {:0>4}, SYM".format(SYMTAB[LITERALTABLE[OPERAND]]))
        continue

    elif OPTAB.get(OPCODE.lstrip('+'), -1) != -1:

        if ',X' in OPERAND:
            nixbpe[2] = 1
            OPERAND = OPERAND.rstrip(',X')

        if OPERAND == '' and OPCODE != 'RSUB':   # format 1
            output_file[-1] += "{:0>2x}".format(OPTAB[OPCODE]).upper()
            print("OPCODE: {:<8} is format 1, object code: {}".format(OPCODE, output_file[-1]))
            LOCCTR += 1

        elif len(OPERAND.rstrip(',X').split(',')) == 2 or OPCODE == 'CLEAR' or OPCODE == 'TIXR':    # format 2
            output_file[-1] += "{:0>2x}".format(OPTAB[OPCODE]).upper()
            LOCCTR += 2
            output_file = format_2(output_file[-1], OPCODE ,OPERAND)
        else:   # format 3/4
            if OPCODE[0] == '+':
                nixbpe[-1] = 1

            if OPERAND == '': # RSUb
                output_file[-1] += "{:0>2x}0000".format(OPTAB[OPCODE]).upper()
                print("OPCODE: {:<8} is format 3/4, object code: {}".format(OPCODE, output_file[-1]))
                continue

            if OPERAND[0] == '@':       # indirect
                nixbpe[0] = 1
                nixbpe[1] = 0
                OPERAND = OPERAND.lstrip('@')
            elif OPERAND[0] == '#':     # immediate
                nixbpe[0] = 0
                nixbpe[1] = 1
                OPERAND = OPERAND.lstrip('#')
            else:                       # direct
                nixbpe[0] = 1
                nixbpe[1] = 1

            output_file[-1] += "{:0>2x}".format(OPTAB[OPCODE.lstrip('+')] + nixbpe[0]*2 + nixbpe[1]).upper()

            if SYMTAB.get(OPERAND, -1) == -1:
                # TODO
                WBTAB[OPERAND] += [index]
                OPERAND = 'A'

            if nixbpe[-1]:  # format 4
                output_file[-1] += str_flag(nixbpe)
                output_file[-1] = format_4(output_file[-1], OPERAND)
            else:   # format 3
                output_file[-1] = format_3(output_file[-1], nixbpe, OPERAND)

            LOCCTR += 3 if OPCODE[0] != '+' else 4


    elif OPCODE == 'WORD':
        LOCCTR += 3
    elif OPCODE == 'RESW':
        LOCCTR += 3 * int(OPERAND)
    elif OPCODE == 'RESB':
        LOCCTR += 1 * int(OPERAND)
    elif OPCODE == 'BYTE':
        matches = re.search(regex, OPERAND)
        if OPERAND[0] == 'X':
            output_file[-1] += matches.groups()[0]
            LOCCTR += math.ceil(len(matches.groups()[0]) * 4 / 24)
        else:  # 'C'
            for char in matches.groups()[0]:
                output_file[-1] += "{:0>2x}".format(ord(char)).upper()
            LOCCTR += len(matches.groups()[0])
        print("OPCODE: {:<8} is Set, object code: {}".format(OPCODE, output_file[-1]))
    else:
        print("unknow opcode, LABEL: {:<8}, OPCODE: {:<8}, OPERAND: {:<8}".format(LABEL, OPCODE, OPERAND))
        exit(187)

    output_file.append(line)



print("\nSYMTAB:")
for item in SYMTAB:
    print("{:<8}: {:0>4x}".format(item, SYMTAB[item]).upper())

print("\nLITERALTABLE")
for value, SYM in LITERALTABLE.items():
    print("{}: {}".format(value, SYM).upper())

#   ====== NIXBPE ====================================

for line in output_file:
    if line == '':
        output_file.remove(line)
print('\n'.join(output_file))
