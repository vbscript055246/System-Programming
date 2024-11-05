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

BASETABLE = []
LITERALTABLE = {}

def get_hash(s):
    output_hash = ""
    temp = abs(hash(s))

    while len(output_hash)< 3 or any([ output_hash[-3:] == V for L, V in  LITERALTABLE.items()]):
        output_hash += chr(temp % 26 + 65)
        temp//=100
    return output_hash[-3:]


def decode(s):
    s = s.lstrip('\t ').rstrip('\n')
    arr = s.split()
    if arr[0] == 'BASE':
        BASETABLE.append(arr[1])
        print("BASE Set: {}".format(BASETABLE[-1]))
        return ["", "", ""]

    if len(arr) == 2:
        if (arr[0] in OPTAB) or (arr[0].lstrip("+") in OPTAB):
            arr = [""] + arr
        else:
            arr = arr + [""]
    elif len(arr) == 1:
        arr = [""] + arr + [""]
    return arr

for i in range(10):
    LITERALTABLE["EOF"+str(i)]  = get_hash("EOF")
    print(LITERALTABLE["EOF"+str(i)])