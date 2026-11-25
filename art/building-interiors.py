"""Paint enterable buildings and outdoor grounds in the game's pixel palette."""
from pathlib import Path
import base64
import json
import random
import struct
import zlib

T = 24
W, H = 12*T, 9*T
OUT = Path('art-build')
OUT.mkdir(exist_ok=True)

FOOD = ['############','#LLCCCCCCLL#','#..........#','#.sTs..sTs.#','#..s....s..#','#..........#','#.sTs..sTs.#','#..........#','#####DD#####']
WORK = ['############','#LLCCCCCCLL#','#..........#','#.TT....TT.#','#..........#','#.LL....LL.#','#..........#','#..........#','#####DD#####']
HALL = ['############','#LLCCCCCCLL#','#..........#','#.TT....TT.#','#.TT....TT.#','#..........#','#.TT....TT.#','#..........#','#####DD#####']
HOME = ['############','#LLCCCCCCLL#','#..........#','#.TT....TT.#','#.TT.......#','#.....sTs..#','#......s...#','#..........#','#####DD#####']
GARDEN = ['############','#LLLCCCCLLL#','#..........#','#.TT....TT.#','#.TT....TT.#','#..........#','#.LL....LL.#','#..........#','#####DD#####']
LAKE = ['############','#LLLCCCCLLL#','#..........#','#.TTT..TTT.#','#.TTT..TTT.#','#.TTT..TTT.#','#.TTT..TTT.#','#..........#','#####DD#####']
CAVE = ['############','#LLCCCCCCLL#','#..........#','#.TT....TT.#','#.TL....LT.#','#..........#','#.LL....LL.#','#..........#','#####DD#####']
STREET = ['############','#LLLCCCCLLL#','#..........#','#.TL....LT.#','#..........#','#.LT....TL.#','#..........#','#..........#','#####DD#####']

# Layout, floor family, furniture, accent color, and description.
SCENES = {
 'farm':(GARDEN,'garden','crop','a9be56','顺着田埂去看猫草畦、谷筐和水槽。'),
 'mine':(CAVE,'cave','ore','84a0a0','矿灯照着矿车、木支架和矿石堆。'),
 'bakery':(WORK,'wood','pastry','cb8872','烤炉旁的工作台摆着糕点与原料。'),
 'cottage':(HOME,'wood','home','b67782','小床、书桌和热茶给栗栗留着位置。'),
 'cafe':(FOOD,'wood','cup','7f9470','吧台煮着热饮，木桌边有软垫和杯碟。'),
 'shop':(HALL,'wood','crate','9d8b58','货架和木箱之间留着通往柜台的过道。'),
 'hospital':(HOME,'stone','bed','80aeb0','诊疗区有病床、药柜和候诊椅。'),
 'school':(HALL,'wood','magic','9d83a5','讲台后是魔法书架，桌上摆着卷轴与水晶。'),
 'gym':(WORK,'stone','weights','78a4a3','训练垫、哑铃架和器材分开放置。'),
 'sora':(FOOD,'wood','hotpot','638aa6','蓝色暖帘、深木餐桌和寿喜锅与店面相呼应。'),
 'cuihu':(LAKE,'garden','water','75a397','沿着交叉堤岸走到湖边，荷叶和亭子倒映在水里。'),
 'kunming':(HALL,'stone','desk','a49e83','校园讲堂内有成排课桌、讲台和资料柜。'),
 'bread':(WORK,'wood','oven','d3a16b','面包炉和藤篮靠墙，柜台摆着刚出炉的面包。'),
 'florist':(WORK,'wood','bouquet','c98d98','花桶、盆栽和包装台分列在两侧。'),
 'inn':(HOME,'wood','inn','8b779d','客房摆着铺好床的床榻、边桌和阅读灯。'),
 'post':(WORK,'wood','mail','7297ae','信格、邮包和分拣台都在一条短动线上。'),
 'library':(HALL,'wood','book','a28c61','书架和阅读桌之间是一条安静的通道。'),
 'glasshouse':(GARDEN,'stone','greenhouse','8fb99d','玻璃窗下摆着育苗托盘和长形种植床。'),
 'bench':(STREET,'garden','bench','a9976b','街角是一处带树荫的休息点。'),
 'sign':(STREET,'garden','sign','b89a66','开放的小路口有木制路牌和树篱。'),
 'streetlight':(STREET,'garden','lamp','dfa45c','灯笼下留了一小片铺石的街角。'),
 'mixc':(HALL,'stone','mall','889fa4','玻璃大堂的两翼设有展柜，中庭留出通行空间。'),
 'flowers':(GARDEN,'garden','flowers','cf8da9','花畦和碎石步道围着小花园。'),
 'fountain':(LAKE,'stone','fountain','85aab3','铺石广场围着喷泉，沿外圈可以散步。'),
 'road':(STREET,'garden','pavers','bca87a','这段碎石小径连着路牌和路边绿植。'),
 'mansion':(HALL,'wood','royal','cca1ac','粉色会客厅有地毯、座椅和通往王座厅的入口。'),
}

def chunk(kind, data):
    return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))

def paint(key, config):
    layout, surface, fixture, accent, _ = config
    canvas = [bytearray(W * 3) for _ in range(H)]
    rnd = random.Random(key)

    def box(x, y, w, h, hue):
        left, right = max(0, x), min(W, x+w)
        if right <= left:
            return
        color = bytes.fromhex(hue)
        for row in range(max(0,y), min(H,y+h)):
            canvas[row][left*3:right*3] = color*(right-left)

    def object_(x,y,w,h,top,side='624837',shadow='745541'):
        box(x+2,y+2,w,h,shadow)
        box(x,y,w,h,side)
        box(x+1,y+1,w-2,h-4,top)
        box(x+2,y+1,w-4,1,'dec496')

    def flower(x,y,hue):
        box(x,y+3,1,7,'486448')
        box(x-1,y+5,3,2,'6f9659')
        box(x-2,y+1,5,3,hue)
        box(x,y,1,5,hue)
        box(x,y+2,1,1,'eed28a')

    def lantern(x,y):
        box(x+3,y-2,1,4,'604335')
        box(x,y+1,7,7,'7c4b38')
        box(x+1,y+2,5,5,'e0a45e')
        box(x+2,y+2,2,4,'f1c879')

    tones = {
        'wood':('ae7e56','b98c61','956443','c59b72','77533e'),
        'stone':('a5a08a','bab19b','87816e','c2baa6','6f766e'),
        'garden':('8b9e5a','9bab66','70884c','adba69','4c6d45'),
        'cave':('736a60','837969','655c57','928574','494b49'),
    }[surface]
    box(0,0,W,H,tones[0])
    for y in range(0,H,6 if surface=='wood' else 12):
        offset=(y//6%3)*11
        for x in range(-offset,W,34 if surface=='wood' else 20):
            line=5 if surface=='wood' else 11
            width=34 if surface=='wood' else 20
            fill=rnd.choice(tones[:3] if surface in ('garden','cave') else tones[:2])
            box(x,y,width-1,line,fill)
            if surface in ('wood','stone'):
                box(x+1,y,width-2,1,tones[3])
                box(x,y+line,width,1,tones[2])
            for _ in range(2):
                box(x+rnd.randrange(2,width),y+rnd.randrange(1,line),rnd.randrange(1,4),1,tones[3])

    # Outer wall/hedge and a lit doorway mark every entrance.
    if surface=='garden':
        box(0,0,W,18,tones[4]);box(0,1,W,3,tones[2])
        box(0,16,13,H-16,tones[4]);box(W-13,16,13,H-16,tones[4])
        for x in range(4,W-6,13):
            box(x,6,9,8,'698953');box(x+2,5,5,3,'829f5a')
        box(115,192,58,24,'af956c');box(119,198,50,3,'d4bd8b')
    else:
        box(0,0,W,24,tones[4]);box(0,4,W,3,tones[3]);box(12,8,W-24,11,tones[1])
        box(0,18,14,H-18,tones[4]);box(W-14,18,14,H-18,tones[4])
        box(2,17,3,H-30,tones[3]);box(W-5,17,3,H-30,tones[3])
        box(0,H-15,W,15,tones[4]);box(119,H-15,50,15,accent);box(119,H-15,50,3,'d7ae7a')
    for x in (29,252):
        lantern(x,13 if surface!='garden' else 19)

    for y, row in enumerate(layout):
        for x, cell in enumerate(row):
            px,py=x*T,y*T
            if cell=='C':
                object_(px,py+2,24,21,accent)
                box(px+2,py+4,20,1,'dec496')
                if x%2==0:box(px+9,py+8,6,4,'ede1b9')
            elif cell=='L':
                if surface=='garden':
                    box(px+3,py+4,18,14,'567a48')
                    box(px+5,py+2,14,12,'779655')
                    if x%2==0:flower(px+12,py+6,accent)
                else:
                    object_(px+2,py+2,20,20,'88694b')
                    for dx in (4,9,14):box(px+dx,py+6,4,6,rnd.choice(['d0ab72',accent,'a77a61']))
            elif cell=='s':
                object_(px+7,py+7,11,11,accent,'5d4839')
            elif cell=='T':
                if fixture in ('water','fountain'):
                    box(px,py,T,T,'bdaf86')
                    box(px+1,py+1,T-2,T-2,'4a8191')
                    box(px+4,py+6,13,2,'81afb1');box(px+9,py+15,11,1,'6e9eab')
                    if fixture=='water' and (x+y)%2==0:
                        box(px+9,py+10,7,4,'6f985d');box(px+11,py+8,3,2,'c891a4')
                    if fixture=='fountain' and (x,y) in ((4,5),(7,5)):
                        object_(px+7,py+4,10,14,'d4c7ac','829698')
                    continue
                if fixture in ('crop','greenhouse','flowers'):
                    object_(px+1,py+4,22,17,'936747','624c36')
                    for dx in (5,12,19):flower(px+dx,py+8,accent)
                    continue
                object_(px+1,py+4,22,17,'bd9664' if surface=='wood' else tones[1])
                if fixture in ('bed','inn','home'):
                    box(px+3,py+5,18,11,accent)
                    box(px+3,py+5,18,3,'ebe2bc')
                    box(px+3,py+15,18,2,'8d765d')
                elif fixture=='ore':
                    box(px+5,py+7,12,8,'4b4f4f')
                    box(px+7,py+8,5,4,accent);box(px+14,py+10,4,3,'a1b3a3')
                elif fixture in ('cup','pastry','hotpot','oven'):
                    box(px+6,py+7,12,8,'62534a');box(px+7,py+7,10,5,accent)
                    box(px+10,py+8,4,2,'e5c492')
                elif fixture in ('bouquet','bench','sign','lamp','pavers'):
                    box(px+3,py+7,17,4,accent)
                    if fixture in ('bouquet','lamp'):flower(px+11,py+6,accent)
                elif fixture=='weights':
                    box(px+5,py+8,14,4,'616367')
                    box(px+6,py+6,3,8,accent);box(px+15,py+6,3,8,accent)
                else:
                    for dx in (4,11):box(px+dx,py+7,6,5,accent)
                    box(px+6,py+7,3,1,'f1db9f')
    if fixture=='ore':
        # Ore rails follow the main corridor to a timber loading frame.
        for y in range(56,190,9):
            box(126,y,36,3,'594a3b')
        for x in (130,157):
            box(x,54,2,136,'a29382')
            box(x,56,1,132,'c2b39a')
        for x in (114,165):
            box(x,26,6,22,'8c6749')
        box(111,25,65,4,'ad835d')
    if fixture in ('bed','inn','home'):
        # Accent textiles and a matching window or clinic sign.
        if fixture=='bed':
            box(136,7,16,13,'ece5c6')
            box(142,9,4,9,'6a9d93');box(139,12,10,3,'6a9d93')
        else:
            box(130,8,28,11,'605c4d')
            box(132,9,24,8,'99aaa0')
            box(143,9,2,8,'dac3a1')
            box(125,144,35,34,accent)
            box(126,146,32,2,'dcbb8c');box(126,173,32,2,'dcbb8c')
    if fixture=='water':
        # A little gold-roof pavilion sits on the upper causeway.
        for y in range(7,23):
            inset=max(0,15-(y-7))*2
            box(118+inset,y,52-2*inset,1,'d5ac61' if y<19 else 'ac7947')
        box(121,23,46,2,'e0c280')
        for x in (125,158):box(x,24,3,12,'a5684b')
        box(123,36,44,2,'d4b884')
    if fixture=='greenhouse':
        box(14,8,W-28,13,'8cb9a7')
        for x in range(17,W-16,12):box(x,8,2,13,'d2d4b2')
        box(15,16,W-30,2,'c7caa7')
    if fixture in ('book','magic'):
        for x in (29,244):
            for y in (28,37):
                for dx in (1,5,9,13):
                    box(x+dx,y,3,5,rnd.choice(['a17663','d3ae76','747d67',accent]))
                box(x,y+6,19,1,'d0a874')
    if fixture=='fountain':
        for x in (97,168):
            box(x,113,25,20,'a89a77')
            box(x+2,115,21,16,'6999a3')
            box(x+10,105,4,21,'b4c7b9')
            box(x+6,109,12,3,'dce0be')
    if fixture=='royal':
        box(126,56,36,123,'99687a');box(127,57,2,121,'d4a498');box(159,57,2,121,'d4a498')
    if fixture=='pavers':
        for y in range(50,190,8):box(119,y,50,6,'b4a17c')
    if fixture=='sign':
        box(58,76,3,20,'6c503b');box(53,76,16,7,accent)
    if fixture=='lamp':
        lantern(61,76);box(64,84,2,14,'6c503b')
    if fixture=='bench':
        box(55,81,16,5,accent);box(56,86,2,5,'6c503b');box(67,86,2,5,'6c503b')
    if fixture=='mall':
        for x in range(17,W-15,18):box(x,8,13,8,'9ebab0')
    raw=b''.join(b'\0'+row for row in canvas)
    header=struct.pack('!IIBBBBB',W,H,8,2,0,0,0)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')

# CSS and collision layouts are intentionally produced together.
css=[]
for key, item in SCENES.items():
    png=base64.b64encode(paint(key,item)).decode('ascii')
    css.append('.henu-board[data-room='+key+']{background-image:url(data:image/png;base64,'+png+');}')
(OUT/'building-interiors.css').write_text('\n'.join(css),encoding='utf-8')
(OUT/'building-interiors.json').write_text(json.dumps({key:{'layout':v[0],'description':v[4]} for key,v in SCENES.items()},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
