import base64, struct, zlib, random
from pathlib import Path

Path("art-build").mkdir(exist_ok=True)
W=32
palette=dict(ink='35433e',shadow='618447',grass='9aba5b',light='afc96b',dark='799e50',sand='dfb679',sandlight='f5ce8c',water='4b93a5',wave='75c3bf',waterdeep='38788e',cream='f5dfa8',plaster='e7bd83',wood='936342',roof='ab514d',roofdark='753f43',rooflight='df7860',window='586071',stone='85868c',stonelight='aeb1ab',stonedark='565a67',leaf='50935b',leaflight='8ab957',leafdark='37674c',gold='efc267',pink='d77b8b',purple='9476a2')
def color(c):
 return bytes.fromhex(palette.get(c,c))+b'\xff'
def picture(): return [bytearray(W*4) for _ in range(W)]
def rect(a,x,y,w,h,c):
 rgb=color(c)
 for j in range(max(0,y),min(W,y+h)):
  for i in range(max(0,x),min(W,x+w)):a[j][i*4:i*4+4]=rgb
def poly(a,points,c):
 for y in range(W):
  ranges=[]
  for (x0,y0),(x1,y1) in zip(points,points[1:]+points[:1]):
   if min(y0,y1)<=y+.5<max(y0,y1):ranges.append(x0+(y+.5-y0)*(x1-x0)/(y1-y0))
  ranges.sort()
  for l,r in zip(ranges[::2],ranges[1::2]):rect(a,int(l),y,int(r)-int(l)+1,1,c)
def encode(a):
 def chunk(tag,b):return struct.pack('!I',len(b))+tag+b+struct.pack('!I',zlib.crc32(tag+b))
 size=len(a)
 raw=b''.join(b'\x00'+row for row in a)
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
 return 'url(data:image/png;base64,'+base64.b64encode(png).decode()+')'
def tree(a,x,y,variant=0):
 rect(a,x+4,y+8,4,8,'wood')
 poly(a,[(x+5,y),(x+8,y+3),(x+10,y+3),(x+12,y+8),(x+11,y+12),(x+2,y+12),(x,y+8),(x+2,y+3)],'leafdark')
 poly(a,[(x+5,y+1),(x+8,y+4),(x+10,y+7),(x+8,y+10),(x+2,y+10),(x+1,y+7),(x+3,y+3)],'leaf')
 rect(a,x+4,y+3,3,3,'leaflight')
 if variant: rect(a,x+8,y+7,2,2,'gold')
def base(n):
 a=picture();rng=random.Random(n)
 rect(a,0,0,32,32,'grass')
 for _ in range(20):
  x,y=rng.randrange(31),rng.randrange(31)
  rect(a,x,y,rng.choice([1,2,3]),1,rng.choice(['dark','light','light']))
 for x,y in [(4,7),(22,22),(10,28)]:
  x=(x+n*9)%27;y=(y+n*5)%27
  rect(a,x,y,3,1,'dark');rect(a,x+1,y-1,1,2,'dark')
 return a
def roof(a,c='roof'):
 poly(a,[(3,17),(13,6),(19,6),(29,17),(27,19),(5,19)],'roofdark')
 poly(a,[(5,16),(14,7),(18,7),(26,16)],c)
 rect(a,12,10,7,1,'rooflight');rect(a,8,14,14,1,'rooflight')
def house(a,c):
 rect(a,5,26,23,3,'shadow')
 rect(a,7,15,19,12,'wood');rect(a,8,16,17,10,'plaster');rect(a,8,18,16,2,'cream')
 roof(a,c)
 rect(a,14,20,5,7,'wood');rect(a,15,21,3,5,'roofdark')
 rect(a,9,20,4,4,'window');rect(a,10,21,2,2,'gold')
 rect(a,21,20,3,4,'window');rect(a,22,21,1,2,'gold')
imgs={}
for n in range(4):imgs['terrain-'+str(n)]=base(n)
wet=[0,8,16,24,32,40,41,42]
for i in wet:
 a=picture(); rect(a,0,0,32,32,'water')
 for j in range(6):
  x=(j*11+i*3)%30;y=(j*7+i*2)%31
  rect(a,x,y,4+(j%3)*3,1,'waterdeep');rect(a,x+2,y+1,4+(j%2)*2,1,'wave')
 if i%8<7 and i+1 not in wet:
  for y in range(0,32,4):
   x=28-((y//4+i)%3)
   rect(a,x,y,32-x,4,'sand');rect(a,x+2,y,32-x-2,4,'dark')
 if i-8>=0 and i-8 not in wet:
  for x in range(0,32,4):
   h=3+((x//4+i)%3)
   rect(a,x,0,4,h,'sand');rect(a,x,0,4,h-2,'dark')
 imgs['water-'+str(i)]=a
a=picture();tree(a,5,4);tree(a,16,7,1);imgs['grove']=a
a=picture();rect(a,10,9,12,11,'leafdark');rect(a,12,7,8,12,'leafdark');rect(a,14,9,4,6,'light');rect(a,10,15,12,8,'wood');rect(a,11,16,10,6,'gold');rect(a,15,17,2,3,'wood');imgs['lock']=a
a=picture();poly(a,[(1,5),(28,5),(31,9),(31,25),(29,28),(3,28),(0,24),(0,9)],'sand');rect(a,4,8,23,1,'sandlight');rect(a,5,24,22,1,'wood')
for x,y in [(4,14),(12,10),(18,17),(25,13),(10,21),(22,23)]:rect(a,x,y,3,2,'sandlight')
imgs['road']=a
a=picture();poly(a,[(3,11),(29,11),(31,15),(28,27),(4,27),(1,23)],'wood');rect(a,4,12,24,12,'936344')
for y in [14,19,24]:
 rect(a,4,y,24,1,'b67c53')
 for x in [6,11,17,23]:
  rect(a,x,y-3,1,4,'leafdark');rect(a,x-1,y-3,3,1,'leaflight');rect(a,x+1,y-4,2,1,'leaf')
imgs['farm']=a
a=picture();poly(a,[(2,24),(5,15),(9,14),(13,8),(21,8),(29,16),(31,25)],'stonedark');poly(a,[(4,23),(7,16),(12,15),(15,9),(21,10),(27,16),(29,23)],'stone')
rect(a,14,16,10,10,'ink');rect(a,12,15,2,11,'wood');rect(a,24,15,2,11,'wood');rect(a,12,14,14,2,'sand');rect(a,5,21,4,3,'stonelight');rect(a,19,11,3,2,'stonelight')
rect(a,2,27,27,1,'shadow');rect(a,4,24,8,2,'stonelight');rect(a,5,24,1,4,'stonedark');rect(a,9,25,1,3,'stonedark');imgs['mine']=a
for key,c in [('bakery','roof'),('cafe','purple')]:
 a=picture();house(a,c);rect(a,21,5,3,8,'wood')
 rect(a,9,17,15,2,'cream')
 for x in range(9,23,4):rect(a,x,17,2,3,'rooflight' if key=='bakery' else 'purple')
 imgs[key]=a
a=picture();rect(a,8,26,17,3,'shadow');rect(a,11,14,12,13,'wood');rect(a,12,15,10,11,'cream');rect(a,15,20,4,7,'wood')
poly(a,[(2,16),(5,11),(8,7),(13,5),(20,5),(26,9),(30,15),(28,19),(4,19)],'roofdark')
poly(a,[(4,15),(8,9),(13,6),(20,6),(25,10),(28,15),(26,17),(5,17)],'rooflight')
for x,y in [(8,13),(16,8),(22,13)]:rect(a,x,y,3,2,'cream')
imgs['cottage']=a
a=picture()
# Garden plinth and paved pool deck.
poly(a,[(2,25),(7,21),(28,21),(31,25),(31,29),(3,29),(1,28)],'7a8a62')
poly(a,[(2,25),(7,22),(27,22),(31,25),(30,28),(3,28)],'f1caad')
rect(a,3,27,27,1,'fae6c9')
# Stepped facade with warm cream trim and pink roof terraces.
rect(a,5,10,24,14,'a84f75')
rect(a,6,11,22,12,'ed95b4')
rect(a,6,20,22,3,'d86e9a')
rect(a,4,10,26,2,'fff0d9')
rect(a,5,9,24,1,'d866a0')
rect(a,8,4,15,7,'a84f75')
rect(a,9,5,13,5,'e78aae')
rect(a,7,4,17,1,'fff0d9')
rect(a,8,3,15,1,'de72a5')
rect(a,23,7,5,1,'d96c9b')
for x in [23,25,27]:rect(a,x,8,1,2,'fff0d9')
# Tall teal windows, balcony rails and double doors.
for x in [8,21]:
 rect(a,x,13,6,7,'fff0d9')
 rect(a,x+1,14,4,5,'5f8e9d')
 rect(a,x+1,14,4,1,'a8d0cb')
 rect(a,x+3,14,1,5,'cde2d3')
rect(a,12,6,7,3,'fbe6d4')
rect(a,13,6,5,2,'76a6ab')
rect(a,15,6,1,2,'cde2d3')
rect(a,15,14,5,10,'a84f75')
rect(a,16,15,3,8,'e881ad')
rect(a,17,17,2,2,'f9cab1')
rect(a,17,21,1,1,'f9e0a6')
rect(a,14,24,7,1,'fff0d9')
# Aqua pool, pale coping and potted flowers.
rect(a,20,24,10,4,'fff0d9')
rect(a,21,25,8,2,'51aeb2')
rect(a,23,25,3,1,'a5e5d8')
for x in [5,25]:
 rect(a,x,22,3,2,'a85f73')
 rect(a,x,21,3,1,'5e925f')
 rect(a,x+1,20,1,2,'f4c074')
imgs['hall']=a
a=picture();poly(a,[(3,17),(27,17),(30,23),(25,27),(6,27),(2,23)],'wood');rect(a,5,18,22,5,'sand')
for x,y,c in [(8,15,'pink'),(15,11,'cream'),(23,14,'gold'),(19,17,'purple'),(12,18,'rooflight')]:
 rect(a,x,y,2,7,'leafdark');rect(a,x-2,y,6,2,c);rect(a,x,y-2,2,6,c);rect(a,x,y,2,2,'gold')
imgs['flowers']=a
a=picture();poly(a,[(4,17),(27,17),(30,22),(26,27),(7,27),(2,22)],'stonedark');rect(a,5,19,22,5,'stonelight');rect(a,7,20,18,3,'water');rect(a,14,13,4,9,'stone');rect(a,12,12,8,2,'stonelight');rect(a,15,7,2,5,'wave');rect(a,11,9,2,3,'water');rect(a,20,9,2,3,'water');imgs['fountain']=a
a=picture();tree(a,7,5);tree(a,16,11);imgs['forest']=a
for key,c in [('shop','leaf'),('hospital','stonelight'),('school','purple'),('gym','water'),('henu','roof'),('sora','purple')]:
 a=picture();house(a,c)
 if key=='shop':
  rect(a,5,15,23,3,'cream')
  for x in range(6,28,4):rect(a,x,15,2,3,'leaf')
  rect(a,7,22,4,5,'wood');rect(a,8,22,2,2,'gold')
 elif key=='hospital':
  rect(a,13,8,7,6,'cream')
  rect(a,16,8,1,5,'roof');rect(a,14,10,5,1,'roof')
 elif key=='school':
  rect(a,14,5,5,8,'purple');rect(a,15,3,3,9,'gold')
  rect(a,13,6,7,2,'gold');rect(a,15,6,3,2,'cream')
 elif key=='gym':
  rect(a,11,10,11,2,'stonedark')
  for x in [10,13,20,23]:rect(a,x,8,2,6,'stonedark')
 else:
  rect(a,11,13,12,2,'ink');rect(a,13,15,8,2,'ink')
  rect(a,14,11,1,2,'cream');rect(a,18,10,1,3,'cream')
  for x in [6,25]:
   rect(a,x,18,3,5,'roofdark');rect(a,x+1,19,2,3,'gold' if key=='henu' else 'wave')
 imgs[key]=a
# Sukiyaki restaurants: a warm wooden machiya and a blue-noren courtyard.
for key,wall,roof_color,noren in [('henu','b98053','4d424e','b94342'),('sora','e0cfac','475768','345b86')]:
 a=picture()
 rect(a,2,27,28,3,'shadow')
 rect(a,4,23,24,4,'stone')
 rect(a,4,26,24,1,'stonelight')
 rect(a,5,11,22,13,'453939')
 rect(a,6,12,20,11,wall)
 for x in (6,12,20,25):rect(a,x,12,1,12,'wood')
 for x in (7,21):
  rect(a,x,15,4,6,'473c43')
  rect(a,x+1,16,2,4,'gold')
  rect(a,x+2,16,1,4,'wood')
 poly(a,[(2,14),(5,10),(8,9),(12,5),(20,5),(25,10),(28,11),(30,14)],'35404d')
 poly(a,[(4,13),(7,10),(10,9),(13,6),(19,6),(24,10),(27,11),(28,13)],roof_color)
 rect(a,11,6,10,1,'stonelight')
 rect(a,4,12,24,1,'85868c')
 rect(a,1,14,30,1,'35383f')
 rect(a,13,15,7,9,'453939')
 for x in (13,16,19):rect(a,x,15,2,4,noren)
 rect(a,15,17,1,2,'cream')
 rect(a,18,17,1,2,'cream')
 rect(a,14,23,6,1,'cream')
 if key=='henu':
  for x in (3,26):
   rect(a,x+1,15,1,2,'wood')
   rect(a,x,17,3,5,'roofdark')
   rect(a,x+1,17,1,4,'rooflight')
   rect(a,x,21,3,1,'gold')
 else:
  rect(a,25,25,5,2,'water')
  rect(a,26,25,3,1,'wave')
  tree(a,25,16)
 imgs[key]=a
for key in ('alpine','desert','steppe','rainforest','tundra','wetland','volcanic','coast','meadow','ocean'):
 a=picture()
 if key in ('alpine','tundra','volcanic'):
  poly(a,[(2,25),(11,9),(17,23),(20,7),(30,25)],'stone' if key!='volcanic' else 'roofdark')
  poly(a,[(6,17),(11,9),(15,17),(12,16),(11,19),(9,16)],'cream')
  poly(a,[(15,16),(20,7),(25,16),(21,16),(20,19),(18,15)],'cream' if key!='volcanic' else 'rooflight')
  if key=='volcanic':rect(a,20,5,2,5,'rooflight');rect(a,21,4,3,1,'rooflight')
 if key in ('rainforest','wetland','meadow'):
  tree(a,4,6);tree(a,14,9,1)
  if key=='wetland':
   rect(a,6,23,21,2,'water');rect(a,9,25,17,2,'wave')
 if key in ('desert','steppe','coast','ocean'):
  for x,y,w in [(6,17,15),(15,20,10),(7,23,10),(4,12,9)]:
   rect(a,x,y,w,1,'wave' if key=='ocean' else 'sandlight')
  if key=='desert':
   rect(a,18,12,3,12,'leafdark');rect(a,14,15,3,5,'leaf');rect(a,16,18,5,2,'leaf')
 imgs['biome-'+key]=a
for key,fur,spot in [('cow','f7e8cd','554553'),('cat','f4ad68','a06351'),('dog','dba46b','805741'),('giraffe','e9b75e','a46647')]:
 a=picture()
 rect(a,4,27,25,2,'shadow')
 if key=='giraffe':
  rect(a,6,16,17,9,fur);rect(a,19,7,5,17,fur);rect(a,20,5,8,7,fur)
  rect(a,22,2,2,4,spot);rect(a,26,2,2,4,spot)
  rect(a,8,23,3,5,spot);rect(a,17,23,3,5,spot)
  for x,y in [(8,18),(13,21),(18,16),(20,11)]:rect(a,x,y,3,2,spot)
  rect(a,26,7,2,2,'ink')
 else:
  rect(a,6,14,17,11,fur);rect(a,8,23,4,5,spot);rect(a,18,23,4,5,spot)
  rect(a,5,14,2,8,spot);rect(a,3,12,3,3,spot)
  rect(a,18,9,11,12,fur)
  rect(a,17,8,4,5,spot);rect(a,27,8,3,5,spot)
  rect(a,22,13,2,2,'ink');rect(a,27,13,2,2,'ink')
  rect(a,23,16,5,3,'pink');rect(a,25,16,1,1,'ink')
  if key=='cow':
   rect(a,11,15,5,5,spot);rect(a,6,19,4,3,spot);rect(a,19,6,2,3,'cream');rect(a,26,6,2,3,'cream')
  if key=='cat':
   rect(a,17,5,3,5,fur);rect(a,27,5,3,5,fur);rect(a,19,8,1,3,'pink');rect(a,28,8,1,3,'pink')
  if key=='dog':rect(a,17,10,3,7,spot);rect(a,28,10,3,7,spot)
 imgs['actor-'+key]=a
for key,robe,hair in [('hero','c55a94','5a363f'),('advisor','567d82','443945')]:
 a=picture()
 rect(a,8,27,17,2,'shadow');rect(a,11,25,4,3,'ink');rect(a,18,25,4,3,'ink')
 poly(a,[(11,16),(21,16),(25,25),(8,25)],robe)
 rect(a,11,6,11,11,hair);rect(a,12,9,9,7,'f7c799');rect(a,13,11,2,2,'ink');rect(a,18,11,2,2,'ink');rect(a,15,15,3,1,'pink')
 rect(a,11,19,11,2,'gold' if key=='hero' else 'cream')
 if key=='hero':
  rect(a,10,5,13,3,'gold')
  for x,y in [(10,2),(16,1),(21,2)]:rect(a,x,y,2,4,'gold')
  rect(a,16,5,2,2,'roof')
 else:
  rect(a,9,5,15,3,'ink');rect(a,12,2,9,4,'ink')
  rect(a,21,17,6,6,'cream');rect(a,22,19,4,1,'wood')
 imgs['actor-'+key]=a
W=64
a=picture()
poly(a,[(2,52),(11,43),(54,43),(63,53),(57,60),(7,60)],'54704a')
poly(a,[(4,52),(13,44),(52,44),(60,52),(53,57),(10,57)],'c7ad79')
rect(a,27,48,12,15,'dfb679')
rect(a,15,26,34,23,'986879')
rect(a,16,27,32,20,'efd5b7')
rect(a,16,45,32,3,'c89b96')
rect(a,23,16,18,16,'a87289')
rect(a,24,17,16,16,'f5ddc3')
poly(a,[(21,18),(32,4),(43,18)],'793f64')
poly(a,[(24,16),(32,7),(41,16)],'bb638b')
rect(a,27,15,9,1,'e58fa9')
rect(a,32,0,1,8,'6f4970')
rect(a,33,1,9,4,'df82a0')
for x,y in [(6,24),(47,24)]:
 rect(a,x,y,11,25,'996775');rect(a,x+1,y+1,8,22,'eed0b2')
 rect(a,x+1,y+17,8,2,'e2b6a3')
 poly(a,[(x-2,y+2),(x+5,y-13),(x+12,y+2)],'754668')
 poly(a,[(x,y),(x+5,y-11),(x+10,y)],'be739b')
 rect(a,x+4,y+4,3,7,'576d78');rect(a,x+4,y+4,1,7,'9ab5b0')
 rect(a,x+5,y-16,1,4,'785875');rect(a,x+6,y-16,5,2,'df82a0')
for x,y in [(18,31),(24,31),(36,31),(42,31),(28,20),(35,20)]:
 rect(a,x,y,4,8,'a37884');rect(a,x+1,y+1,2,6,'669299')
 rect(a,x+1,y+1,2,1,'a7c6b5')
rect(a,28,40,9,9,'764f69');rect(a,30,38,5,4,'764f69')
rect(a,29,42,7,7,'a36a7f');rect(a,32,41,1,8,'f0b594')
rect(a,26,49,13,2,'f4dbc0')
for x in (12,48):tree(a,x,45,1)
rect(a,18,50,8,5,'f6dcb9');rect(a,19,51,6,3,'65a9a9')
rect(a,41,50,8,5,'f6dcb9');rect(a,42,51,6,3,'65a9a9')
imgs['citadel']=a
W=32
for key in ['farm','mine','bakery','cottage','cafe','shop','hospital','school','gym','henu','sora','flowers','fountain','road','citadel']:
 original=imgs[key]
 W=len(original)
 for grade in (2,3):
  a=[row.copy() for row in original]
  cap=grade==3
  if key=='citadel':
   for x in (6,47):
    rect(a,x+1,34,8,2,'f3d591');rect(a,x+1,41,8,2,'f3d591')
   rect(a,16,28,32,2,'f3d591')
   rect(a,22,52,4,2,'wave');rect(a,43,51,5,2,'wave')
   if cap:
    for x in (6,47):
     poly(a,[(x-2,26),(x+5,11),(x+12,26)],'714f79')
     poly(a,[(x,25),(x+5,14),(x+10,25)],'df91b3')
     rect(a,x+2,36,7,2,'ffe0a1')
    rect(a,28,39,9,2,'ffe0a1');rect(a,30,1,3,7,'ffe0a1')
    rect(a,34,1,10,4,'rooflight')
  elif key=='farm':
   for x in (1,28):rect(a,x,11,2,15,'wood');rect(a,x,11,2,2,'sandlight')
   rect(a,3,12,25,1,'sand')
   if cap:
    rect(a,4,8,23,2,'leafdark');rect(a,7,6,16,2,'leaf')
    rect(a,7,26,19,2,'sandlight')
    for x in (6,13,20,27):rect(a,x,16,2,2,'gold');rect(a,x,22,2,2,'gold')
  elif key=='mine':
   rect(a,9,16,3,11,'sand');rect(a,24,16,3,11,'sand')
   rect(a,11,14,15,2,'cream');rect(a,8,26,16,1,'stonelight')
   if cap:
    rect(a,7,18,2,6,'wood');rect(a,27,18,2,6,'wood')
    for x,y in [(6,18),(27,18),(12,11),(22,10)]:
     rect(a,x,y,3,2,'gold');rect(a,x+1,y-1,1,4,'cream')
  elif key=='flowers':
   for x,y,c in [(4,16,'purple'),(11,13,'gold'),(26,17,'pink')]:
    rect(a,x,y,1,6,'leafdark');rect(a,x-1,y,3,2,c)
   if cap:
    poly(a,[(5,22),(8,14),(16,9),(23,14),(27,22),(24,22),(21,15),(16,12),(10,15),(8,22)],'leaf')
    rect(a,14,10,4,2,'cream')
  elif key=='fountain':
   rect(a,10,10,12,2,'stonelight');rect(a,13,9,6,1,'wave')
   if cap:
    rect(a,15,4,2,6,'wave')
    rect(a,12,6,3,2,'wave');rect(a,17,6,3,2,'wave')
    rect(a,4,23,24,1,'cream')
  elif key=='road':
   rect(a,4,9,24,2,'sandlight');rect(a,4,23,24,2,'wood')
   if cap:
    for y in (13,19):
     for x in range(2,29,5):rect(a,x,y,4,2,'cream')
  elif key in ('henu','sora'):
   for x in (6,23):rect(a,x,21,4,3,'wood');rect(a,x,20,4,1,'leaf')
   rect(a,5,12,23,1,'stonelight')
   if cap:
    rect(a,11,7,10,2,'roofdark');rect(a,13,5,7,2,'stone')
    rect(a,14,6,4,1,'gold')
    for x in (3,27):rect(a,x,20,3,2,'gold')
  else:
   for x in (7,23):rect(a,x,24,3,3,'wood');rect(a,x,23,3,1,'leaflight')
   rect(a,11,16,11,1,'cream')
   if cap:
    rect(a,10,7,13,1,'gold');rect(a,8,11,16,1,'gold')
    rect(a,5,25,23,2,'cream')
    rect(a,4,23,2,4,'gold');rect(a,27,23,2,4,'gold')
  imgs[key+'-tier-'+str(grade)]=a
W=32
for key in ('hero','advisor','cow','cat','dog','giraffe'):
 sprite=imgs['actor-'+key]
 walking=[row.copy() for row in sprite]
 if key in ('hero','advisor'):
  rect(walking,10,24,4,4,'ink');rect(walking,20,25,4,2,'ink')
  rect(walking,9,20,3,3,'f7c799')
  back=[row.copy() for row in sprite]
  hair='5a363f' if key=='hero' else '443945'
  rect(back,12,8,9,8,hair)
  rect(back,12,15,9,2,'a65a81' if key=='hero' else '567d82')
  rect(back,15,17,3,8,'e8b070' if key=='hero' else 'd1cdb1')
  imgs['actor-'+key+'-back']=back
 else:
  fur={'cow':'554553','cat':'a06351','dog':'805741','giraffe':'a46647'}[key]
  rect(walking,7,24,3,5,fur);rect(walking,20,23,4,3,fur)
  rect(walking,14,26,3,1,'shadow')
 imgs['actor-'+key+'-step']=walking
W=64
for grade in (1,2,3):
 a=picture()
 bank=[(2,21),(8,14),(51,13),(59,19),(62,46),(55,56),(12,56),(3,50)]
 poly(a,bank,'4c7551')
 poly(a,[(4,22),(9,17),(51,16),(57,21),(59,44),(53,53),(13,53),(5,48)],'94aa67')
 poly(a,[(7,25),(13,19),(48,18),(55,23),(56,43),(49,50),(15,50),(8,46)],'276e79')
 for x,y,w in [(11,28,14),(39,28,10),(12,43,13),(41,46,10),(17,47,6),(39,35,11)]:
  rect(a,x,y,w,2,'408e91');rect(a,x+2,y,w//2,1,'7ab3a1')
 rect(a,29,17,5,35,'d7ae77');rect(a,8,34,48,5,'e7c894')
 rect(a,9,38,45,1,'8d8c62')
 rect(a,24,29,16,13,'71824d')
 rect(a,22,34,20,6,'cab083');rect(a,24,35,16,4,'e7d2a1')
 rect(a,26,25,2,12,'9c5f51');rect(a,35,25,2,12,'9c5f51')
 rect(a,28,29,7,7,'608779')
 poly(a,[(20,27),(25,24),(32,17),(39,24),(44,27),(39,29),(24,29)],'775842')
 poly(a,[(22,26),(26,23),(32,18),(38,23),(42,26),(38,27),(25,27)],'d8ab5b')
 rect(a,28,23,10,1,'efcd81');rect(a,31,16,3,3,'cf9b51')
 for x,y in [(8,22),(47,25),(15,51),(51,48),(8,47)]:
  tree(a,x,y-12,1)
 for x,y in [(19,29),(44,42),(16,44),(53,31)]:
  rect(a,x,y,5,2,'609457');rect(a,x+1,y-2,3,2,'d78392')
 if grade>=2:
  for x in (17,25,38,46):rect(a,x,33,2,2,'e6c281')
  for x,y in [(15,24),(44,30),(19,45),(41,45)]:rect(a,x,y,4,1,'cream');rect(a,x+3,y-1,2,1,'cream')
 if grade==3:
  rect(a,25,39,14,2,'edcf89')
  for x,y in [(15,37),(45,37),(30,42),(33,18)]:rect(a,x,y,2,4,'a26b49');rect(a,x,y,2,2,'f6d58a')
 imgs['cuihu'+('' if grade==1 else '-tier-'+str(grade))]=a
for grade in (1,2,3):
 a=picture()
 poly(a,[(1,48),(10,41),(54,41),(63,49),(62,57),(3,57)],'526e51')
 poly(a,[(3,49),(11,43),(53,43),(61,49),(58,55),(6,55)],'b8b891')
 rect(a,4,18,18,25,'777878');rect(a,42,18,18,25,'777878')
 rect(a,6,16,16,24,'d9d7c6');rect(a,42,16,16,24,'d9d7c6')
 rect(a,20,10,24,36,'8c8a82');rect(a,22,9,20,35,'e6dfc9')
 rect(a,21,7,22,3,'bbb6a7');rect(a,26,5,12,3,'d6d2be')
 rect(a,24,11,16,2,'f4ead7')
 for x in (7,12,17,44,49,54):
  for y in (20,26,32):rect(a,x,y,3,4,'586e72');rect(a,x,y,3,1,'97a9a2')
 rect(a,6,15,14,1,'f2e5cc');rect(a,44,15,14,1,'f2e5cc')
 poly(a,[(25,44),(25,27),(28,21),(32,19),(36,21),(39,27),(39,44)],'727d7b')
 poly(a,[(27,43),(27,28),(30,24),(32,23),(34,24),(37,28),(37,43)],'496970')
 rect(a,31,25,2,17,'72959a');rect(a,26,33,12,1,'829d98')
 rect(a,23,44,18,2,'e8e0cb');rect(a,21,46,22,2,'c6bea8');rect(a,18,49,27,2,'b5aa91')
 for x in (5,56):
  rect(a,x,37,2,10,'796345')
  for dx,dy in [(-4,0),(-2,-2),(1,-3),(3,0)]:rect(a,x+dx,37+dy,5,2,'4e7b59')
 poly(a,[(20,55),(23,50),(39,50),(44,55),(39,58),(22,58)],'888d83')
 for x in (24,28,32,36):rect(a,x,53,2,2,'b7554d')
 if grade>=2:
  for x in (8,13,18,45,50,55):rect(a,x,27,2,2,'e7c97e')
  for x in (9,47):rect(a,x,49,7,3,'67925c');rect(a,x+1,48,5,1,'b98782')
 if grade==3:
  rect(a,24,12,16,1,'fff0c9');rect(a,22,42,20,1,'e7c97e')
  for x in (16,45):rect(a,x,42,1,9,'706446');rect(a,x-1,42,3,2,'e7c97e')
 imgs['kunming'+('' if grade==1 else '-tier-'+str(grade))]=a
W=32
for key,roofcolor in [('bread','roof'),('florist','leaf'),('inn','purple'),('post','water'),('library','stonedark'),('glasshouse','water'),('bench','wood'),('sign','wood'),('streetlight','wood')]:
 for grade in (1,2,3):
  a=picture()
  if key=='bench':
   rect(a,5,26,24,2,'shadow');rect(a,8,20,2,7,'ink');rect(a,23,20,2,7,'ink')
   rect(a,6,14,22,8,'wood');rect(a,7,15,20,2,'sandlight');rect(a,6,20,22,2,'plaster')
   if grade>=2:rect(a,5,18,4,5,'stonedark');rect(a,25,18,4,5,'stonedark')
   if grade==3:rect(a,11,16,12,3,'pink')
  elif key=='sign':
   rect(a,10,27,14,1,'shadow');rect(a,15,7,3,21,'wood')
   poly(a,[(5,10),(24,10),(29,13),(24,16),(5,16)],'sand')
   rect(a,7,12,14,1,'wood')
   if grade>=2:poly(a,[(5,20),(10,17),(25,17),(25,22),(10,22)],'plaster')
   if grade==3:rect(a,14,7,5,3,'gold');rect(a,10,19,12,1,'wood')
  elif key=='streetlight':
   rect(a,10,27,15,1,'shadow');rect(a,15,8,3,19,'stonedark');rect(a,12,24,9,3,'stone')
   rect(a,11,7,11,10,'stonedark');rect(a,12,8,9,7,'gold')
   poly(a,[(10,8),(16,3),(23,8)],'roofdark')
   if grade>=2:rect(a,13,9,7,5,'cream');rect(a,15,4,3,2,'gold')
   if grade==3:rect(a,10,16,13,2,'gold');rect(a,12,24,9,1,'gold')
  elif key=='glasshouse':
   rect(a,3,25,27,3,'shadow');rect(a,5,14,23,12,'leafdark');rect(a,6,15,21,10,'92c4ae')
   poly(a,[(4,15),(13,6),(20,6),(29,15)],'608a78')
   poly(a,[(6,14),(14,7),(19,7),(27,14)],'a9cebb')
   for x in (8,15,23):rect(a,x,14,1,11,'cream')
   rect(a,6,20,21,1,'cream')
   for x in (9,17,23):rect(a,x,22,4,3,'leaf')
   if grade>=2:rect(a,5,13,23,2,'cream')
   if grade==3:rect(a,10,9,13,2,'cream');rect(a,16,15,5,11,'leafdark');rect(a,17,16,3,8,'wave')
  else:
   house(a,roofcolor)
   if key=='bread':rect(a,12,15,9,3,'gold');rect(a,15,16,4,1,'sandlight')
   if key=='florist':
    for x,c in [(6,'pink'),(12,'gold'),(23,'purple')]:rect(a,x,21,3,5,'leafdark');rect(a,x-1,20,5,2,c)
   if key=='inn':
    rect(a,4,12,5,5,'wood');rect(a,5,13,3,3,'gold')
    rect(a,24,18,5,7,'plaster');rect(a,25,19,3,5,'window')
   if key=='post':
    rect(a,11,15,11,5,'cream');rect(a,14,17,5,1,'water')
    rect(a,25,21,4,5,'roofdark');rect(a,25,22,4,1,'cream')
   if key=='library':
    rect(a,9,17,15,3,'cream')
    for x in (9,14,19,23):rect(a,x,20,1,6,'stonelight')
   if grade>=2:rect(a,10,11,12,1,'cream');rect(a,7,24,3,2,'leaf');rect(a,23,24,3,2,'leaf')
   if grade==3:rect(a,7,26,19,1,'gold');rect(a,5,19,2,5,'gold');rect(a,26,19,2,5,'gold')
  imgs[key+('' if grade==1 else '-tier-'+str(grade))]=a
W=64
for grade in (1,2,3):
 a=picture()
 # Light-colored terraces wrap a blue glass corner.
 poly(a,[(2,47),(14,41),(53,41),(62,47),(61,56),(8,59),(2,55)],'547451')
 poly(a,[(4,48),(15,43),(53,43),(60,48),(58,54),(9,56),(4,54)],'ccc4ac')
 poly(a,[(7,15),(47,14),(58,19),(58,44),(49,49),(7,45)],'657277')
 poly(a,[(9,16),(46,15),(56,20),(56,43),(49,47),(9,44)],'8ba6a5')
 poly(a,[(7,15),(14,11),(47,11),(53,14),(57,19),(48,17),(7,18)],'d0c4ad')
 poly(a,[(13,12),(19,8),(44,8),(50,12),(45,15),(11,15)],'beb399')
 rect(a,20,7,24,2,'e8dac1');rect(a,21,7,7,2,'6c985c');rect(a,33,7,9,2,'67945b')
 for level in (20,27,34,41):
  poly(a,[(8,level),(48,level-1),(57,level+4),(56,level+6),(48,level+2),(8,level+3)],'e0d4b7')
  rect(a,10,level+1,36,1,'f3e5cb')
 for x in range(13,54,6):
  rect(a,x,21+(x>47)*3,1,21,'61777c')
 rect(a,11,19,16,5,'54616c');rect(a,12,20,14,3,'b58676')
 rect(a,31,23,12,7,'465c63');rect(a,33,25,8,1,'f4e8cf');rect(a,34,27,6,1,'cec5b5')
 rect(a,28,36,16,10,'4b6f74');rect(a,31,36,11,2,'bed0c1')
 for x in (31,37,41):rect(a,x,38,1,7,'a6b9ad')
 for x,y in [(7,47),(49,50),(53,48),(16,51)]:
  rect(a,x,y,7,4,'86956a');rect(a,x+1,y+1,5,2,'709b64')
 if grade>=2:
  rect(a,11,30,9,4,'9e8270');rect(a,12,31,7,2,'e4bf79')
  rect(a,48,25,6,3,'b8d7c6');rect(a,22,9,5,2,'b58683')
 if grade==3:
  rect(a,27,8,10,2,'84ab65');rect(a,9,42,16,2,'f4d398')
  rect(a,45,41,9,2,'f4d398');rect(a,29,47,14,1,'eed8b4')
 imgs['mixc'+('' if grade==1 else '-tier-'+str(grade))]=a
W=32
for key,stone,highlight,style in [('ridge','85868c','eff0df','alpine'),('tundra','a2b0a7','f1eee1','snow'),('volcano','765e64','d89261','volcanic')]:
 a=picture()
 poly(a,[(2,25),(6,18),(12,6),(17,15),(21,9),(30,25),(28,28),(5,28)],'565a67')
 poly(a,[(4,24),(12,7),(18,24)],stone)
 poly(a,[(12,7),(17,16),(20,25),(15,25)],'69737a' if key!='volcano' else '654d55')
 poly(a,[(15,25),(21,10),(28,25)],stone)
 poly(a,[(9,14),(12,7),(16,15),(12,13)],highlight)
 poly(a,[(19,16),(21,10),(24,17),(22,15)],highlight)
 rect(a,7,24,13,1,'aeb1ab');rect(a,17,26,9,1,'35433e')
 imgs['terrain-'+key]=a
a=picture()
tree(a,6,4,1);tree(a,14,11)
rect(a,9,27,17,2,'shadow');rect(a,13,24,2,4,'wood')
imgs['terrain-tree']=a
a=picture()
poly(a,[(1,22),(7,13),(14,9),(23,11),(30,18),(31,24),(23,29),(8,28)],'536b47')
poly(a,[(3,20),(8,13),(15,9),(23,12),(28,18),(26,21),(11,24)],'77994e')
poly(a,[(7,17),(11,12),(16,10),(23,13),(25,17),(18,19),(9,20)],'a8ba68')
poly(a,[(5,22),(11,23),(20,21),(28,18),(29,23),(24,27),(9,27)],'9a805d')
rect(a,9,24,8,1,'c3a774');rect(a,18,23,7,1,'c3a774')
rect(a,9,26,11,1,'85684f');rect(a,20,25,5,1,'85684f')
rect(a,13,13,6,1,'c4cf81');rect(a,10,16,4,1,'b9c679')
imgs['relief-rise']=a
css=[]
for name,a in imgs.items():
 if name.startswith(('terrain','water')):selector='.tile.'+name;prop='background-image'
 else:selector='.pixel-'+name;prop='background-image'
 css.append(selector+'{'+prop+':'+encode(a)+'}')
Path('art-build/pixel.css').write_text('\n'.join(css))
