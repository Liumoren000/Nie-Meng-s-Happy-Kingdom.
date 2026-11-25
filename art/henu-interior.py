"""Paint the Henu restaurant room at its native pixel resolution."""
from pathlib import Path
import random
import struct
import zlib

TILE = 24
WIDTH, HEIGHT = TILE * 12, TILE * 9
canvas = [bytearray(WIDTH * 3) for _ in range(HEIGHT)]
rng = random.Random(83)

def rect(x, y, width, height, color):
    fill = bytes.fromhex(color)
    left, right = max(0, x), min(WIDTH, x + width)
    if right <= left:
        return
    for row in range(max(0, y), min(HEIGHT, y + height)):
        canvas[row][3 * left:3 * right] = fill * (right - left)

def octagon(x, y, width, height, color):
    rect(x + 2, y, width - 4, height, color)
    rect(x, y + 2, width, height - 4, color)

def bowl(x, y, color='e1c594'):
    rect(x + 1, y + 1, 5, 5, '3f3026')
    octagon(x, y, 7, 5, color)
    rect(x + 2, y + 1, 3, 2, '73594a')
    rect(x + 2, y + 1, 2, 1, 'facb81')

def plant(x, y):
    rect(x - 3, y + 6, 9, 2, '69492d')
    octagon(x - 3, y + 2, 8, 5, 'a66647')
    rect(x, y - 5, 1, 9, '3c5536')
    rect(x - 4, y - 4, 4, 3, '597743')
    rect(x + 1, y - 7, 4, 4, '7a9353')
    rect(x + 1, y - 6, 2, 1, '9ba864')

def lantern(x, y):
    rect(x + 3, y - 5, 1, 5, '745039')
    octagon(x, y, 8, 11, '8b5140')
    rect(x + 1, y + 2, 6, 7, 'dda053')
    rect(x + 2, y + 3, 3, 5, 'f5c475')
    rect(x + 1, y + 8, 6, 2, 'b56743')
    rect(x + 3, y + 11, 1, 4, 'ac7350')

# Floorboards lead to the counter. Grain is drawn with short pixel fragments.
rect(0, 0, WIDTH, HEIGHT, '49342d')
floor = ['ae7c52', 'b78658', 'b18054', 'a5744d', 'ba8a5c']
for row, y in enumerate(range(32, 201, 6)):
    for x in range(17 - (row % 3) * 15, 270, 46):
        color = rng.choice(floor)
        rect(x, y, 45, 5, color)
        rect(x, y + 5, 46, 1, '946543')
        rect(x + 2, y, 40, 1, 'c19162')
        for _ in range(4):
            offset = rng.randrange(1, 40)
            rect(x + offset, y + rng.randrange(1, 5), rng.randrange(1, 6), 1,
                 rng.choice(['a87951', 'b88659', 'c39768']))
rect(18, 44, 252, 5, '95623f')
rect(18, 49, 252, 2, 'a47047')
rect(14, 194, 260, 11, '604333')

# Raised timber skirting and cream wall above the bar.
rect(0, 0, WIDTH, 29, '704835')
rect(0, 3, WIDTH, 4, 'b18454')
rect(11, 8, 266, 16, 'e1bc86')
for x in range(14, 276, 13):
    rect(x, 9, 1, 14, 'c69e6b')
rect(0, 22, WIDTH, 4, 'a97749')
rect(0, 25, WIDTH, 7, '50382d')
for x in (0, 274):
    rect(x, 1, 14, 203, '765038')
    rect(x + 1, 3, 3, 197, 'a7734a')
    rect(x + 10, 2, 4, 201, '593b30')
    for y in range(29, 193, 22):
        rect(x + 4, y, 7, 2, '94623f')
rect(0, 6, WIDTH, 2, '54392c')
rect(18, 30, 252, 1, 'c99760')

# Noren and sign inspired by the restaurant's facade.
rect(113, 8, 62, 3, '65412f')
for x in (116, 130, 144, 158):
    rect(x, 11, 13, 13, 'a95b46')
    rect(x, 13, 13, 2, 'be754f')
    rect(x + 1, 22, 11, 2, '894538')
rect(126, 10, 36, 11, '6c4533')
rect(127, 11, 34, 9, 'a5744b')
for x in (30, 252):
    lantern(x, 12)

# Shelves, condiment jars, and counter.
for x in (25, 244):
    rect(x, 23, 20, 24, '51372b')
    rect(x + 1, 24, 18, 19, '785239')
    for y in (28, 37):
        for dx, tone in ((3, 'd1aa74'), (8, 'a5543c'), (13, '80905a')):
            rect(x + dx, y - 3, 3, 4, tone)
        rect(x + 1, y + 1, 18, 2, 'be8b56')
rect(67, 27, 155, 24, '55402f')
rect(69, 27, 151, 13, 'd3a46b')
rect(69, 27, 151, 2, 'e3bd83')
rect(69, 39, 151, 3, '9d6c43')
rect(69, 43, 151, 7, '83573c')
for x in range(75, 211, 12):
    rect(x, 44, 1, 5, '694730')
for x in (77, 109, 167, 194):
    bowl(x, 31)
for x in (132, 144):
    rect(x, 33, 9, 3, '798355')
    rect(x + 1, 33, 4, 1, 'a6a073')

# Dining tables with inset burners, bowls, utensils, and red upholstered stools.
def table(tx, ty):
    x, y = tx * TILE, ty * TILE
    rect(x + 1, y + 19, 24, 4, '8c5e3c')
    octagon(x + 1, y + 4, 23, 17, '604230')
    octagon(x + 2, y + 3, 21, 15, 'c08c55')
    rect(x + 5, y + 3, 15, 1, 'e1af70')
    octagon(x + 8, y + 6, 8, 8, '5b4b40')
    octagon(x + 9, y + 7, 6, 6, '867269')
    rect(x + 10, y + 8, 4, 2, '554844')
    rect(x + 5, y + 8, 1, 5, 'e5b879')
    rect(x + 18, y + 7, 1, 5, '6b503a')
    rect(x + 18, y + 7, 1, 1, 'ead1a0')

def seat(tx, ty):
    x, y = tx * TILE, ty * TILE
    rect(x + 6, y + 17, 14, 3, '8c5b3d')
    octagon(x + 6, y + 7, 13, 12, '674137')
    octagon(x + 7, y + 6, 11, 10, 'ad5a47')
    rect(x + 9, y + 7, 7, 2, 'cc7960')
    rect(x + 8, y + 14, 9, 1, '9c5243')

for y in (3, 6):
    for x in (3, 8):
        table(x, y)
    for x in (2, 4, 7, 9):
        seat(x, y)
for x in (3, 8):
    seat(x, 4)

# Step, entry runner, and plants remain clear of the walkable doorway.
rect(111, 202, 66, 14, '533a30')
rect(119, 200, 50, 15, 'aa694b')
rect(121, 201, 46, 3, 'cf9160')
rect(123, 206, 42, 6, '92563d')
rect(125, 207, 38, 1, 'c77e50')
for x in (101, 181, 29, 258):
    plant(x, 193)
rect(15, 204, 93, 4, 'ad794b')
rect(181, 204, 92, 4, 'ad794b')
rect(0, 213, WIDTH, 3, '4c362d')

def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))

encoded = b''.join(b'\0' + row for row in canvas)
header = struct.pack('!IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(encoded, 9)) + chunk(b'IEND', b'')
out = Path('art-build')
out.mkdir(exist_ok=True)
(out / 'henu-interior.png').write_bytes(png)
