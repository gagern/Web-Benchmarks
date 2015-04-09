# thanks to evanw for his improvements https://gist.github.com/evanw/11339324

import os
import re
import json
import base64
 
path = 'meminit.json'
data = ''.join(map(chr, json.loads(open(path, 'rb').read())))
print 'data length:', len(data)
 
def tinystr(s):
    hex_to_octal = lambda x: '\\%s' % (oct(int(x.group(1), 16))[1:] or 0)
    s = repr(s)
    s = re.sub(r'\\x([0-1][0-9A-Fa-f])(?:(?=[^0-9])|$)', hex_to_octal, s)
    return s

def tinystrxor(s):
    hex_to_octal = lambda x: '\\%s' % (oct(int(x.group(1), 16))[1:] or 0)
    s = ''.join(chr(ord(x) ^ 32) for x in s)
    s = repr(s)
    s = re.sub(r'\\x([0-1][0-9A-Fa-f])(?:(?=[^0-9])|$)', hex_to_octal, s)
    return s

def tinylut(s):
    data = list(map(ord, s))
    counts = [0]*256
    for b in data:
        counts[b] += 1
    idxs = [i for (c, i) in sorted(((-c, i) for (i, c) in enumerate(counts)))]
    preference = (range(32, 39) + range(40, 92) + range(93, 127) +
                  [39, 92] + range(0, 32) + range(127, 256))
    assert len(preference) == 256
    lu1 = [None]*256
    lu2 = [None]*256
    for a, b in zip(idxs, preference):
        lu1[a] = chr(b) # encode
        lu2[b] = a # decode
    s = tinystr(''.join(lu1[b] for b in data))
    lu = ','.join(map(str, lu2))
    return "[[{}],{}]".format(lu, s)
    
def base88(s):
    membytes = list(map(ord, s))
    membytes.extend([0]*(3 - ((len(membytes) + 3) & 3)))
    assert len(membytes) % 4 == 0
    b88 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+,-./:;=?[]^_`{|}~'
    assert len(b88) == 88
    memstr = ""
    while membytes:
        m1, m2, m3, m4 = membytes[:4]
        assert m1 >= 0 and m2 >= 0 and m3 >= 0 and m4 >= 0
        membytes = membytes[4:]
        c = (m4 << 16) + (m3 << 8) + m2
        if c == 0 and m1 == 0:
            memstr += "@"
            continue
        c5 = b88[c // 234256]
        c4 = b88[(c // 2662) % 88]
        c = ((c % 2662) << 8) + m1
        c3 = b88[c // 7744]
        c2 = b88[(c // 88) % 88]
        c1 = b88[c % 88]
        memstr += c1 + c2 + c3 + c4 + c5
    return memstr

def size(bytes):
    return '%.1f KB' % (bytes / 1000.0)
 
def write(type, data):
    output = path + '.' + type
    file(output, 'wb').write(data)
    os.system('gzip --stdout --best %s > %s.gz' % (output, output))
    gzip = file(output + '.gz', 'rb').read()
    print '| %14s | %17s | %12s |' % (type, size(len(data)), size(len(gzip)))
 
print '| Representation | uncompressed size | gzipped size |'
print '| -------------- | ----------------- | ------------ |'
 
write('binary', data)
write('minstr', tinystr(data))
write('minstrx', tinystrxor(data))
write('str', repr(data))
write('int8', '[' + ','.join(map(str, map(ord, data))) + ']')
write('base64', repr(base64.b64encode(data)))
write('base88', '"' + base88(data) + '"')
write('tinylut', tinylut(data))
 
if 0 == len(data) % 4:
    out = []
    for i in range(0, len(data), 4):
        a = data[i]
        b = data[i+1]
        c = data[i+2]
        d = data[i+3]
        out.append(ord(a) | (ord(b) << 8) | (ord(c) << 16) | (ord(d) << 24))
    write('int32', '[' + ','.join(map(str, out)) + ']')
