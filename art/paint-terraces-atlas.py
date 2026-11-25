import base64, json, math, random, struct, zlib
from array import array
from pathlib import Path

Path("art-build").mkdir(exist_ok=True)
TILE=32
SIZE=TILE*39
island=json.loads(Path('art-build/island-terrain.json').read_text())
terrain={(t['x'],t['y']):t['biome'] for t in island}
palette={
 'water': ['244f6e','2c688d','327da4','4096b6','58aac3','84c7c8','b2d5bb'],
 'meadow':['3f6840','527e43','678f44','78a34b','8bb14d','a6bd59','bdca67'],
 'coast':['927347','b58a50','c69c5a','ddab61','ebbf73','f2cb82','f6dc9a'],
 'alpine':['536575','697f88','81969a','a0afb1','b7c7c6','d4dfd7','eff0df'],
 'tundra':['6e7a81','899493','a5aaa1','b8bdb0','cdd0c1','dee1cb','eae8d5'],
 'desert':['9b654b','b98155','c7905d','d5a56a','e2b77d','e9c486','f2d08c'],
 'steppe':['827a47','9a9157','aaa062','b4aa69','c4ba76','d3c784','ddcf91'],
 'rainforest':['284c40','365b43','427743','49864a','58974d','70aa53','88b45b'],
 'wetland':['405e55','527366','5f8270','729377','82a07e','91ac83','a4ba8c'],
 'volcanic':['52474f','69595c','776261','8a7065','9e7c6d','b78a75','cb9b7d'],
}
rgb=lambda c:bytes.fromhex(c)
colors={key:[rgb(c) for c in values] for key,values in palette.items()}
rows=[bytearray(SIZE*3) for _ in range(SIZE)]
def rect(x,y,w,h,c):
 c=rgb(c) if isinstance(c,str) else c
 x0,x1=max(0,x),min(SIZE,x+w)
 if x0>=x1:return
 for j in range(max(0,y),min(SIZE,y+h)):rows[j][x0*3:x1*3]=c*(x1-x0)
def poly(points,c):
 low=max(0,min(p[1] for p in points))
 high=min(SIZE,max(p[1] for p in points))
 for y in range(low,high):
  xs=[]
  for (x0,y0),(x1,y1) in zip(points,points[1:]+points[:1]):
   if min(y0,y1)<=y+.5<max(y0,y1):xs.append(x0+(y+.5-y0)*(x1-x0)/(y1-y0))
  xs.sort()
  for x0,x1 in zip(xs[::2],xs[1::2]):rect(int(x0),y,int(x1)-int(x0)+1,1,c)
def noise(x,y):
 n=(x*374761393+y*668265263)&0xffffffff
 n=((n^(n>>13))*1274126177)&0xffffffff
 return (n^(n>>16))/0xffffffff
def coarse(x,y,scale):
 gx,gy=x//scale,y//scale
 dx,dy=(x%scale)/scale,(y%scale)/scale
 dx=dx*dx*(3-2*dx);dy=dy*dy*(3-2*dy)
 a=noise(gx,gy)*(1-dx)+noise(gx+1,gy)*dx
 b=noise(gx,gy+1)*(1-dx)+noise(gx+1,gy+1)*dx
 return a*(1-dy)+b*dy
def kind(x,y):return terrain.get((x//TILE,y//TILE),'water')
elevation={(tile['x'],tile['y']):tile['elevation'] for tile in island}
spacing=2
count=SIZE//spacing
field=[]
for gy in range(count):
 y=gy*spacing
 row=array('f')
 for gx in range(count):
  x=gx*spacing
  tx=(x+.5)/TILE-.5;ty=(y+.5)/TILE-.5
  px,py=math.floor(tx),math.floor(ty)
  fx,fy=tx-px,ty-py
  local=elevation.get((x//TILE,y//TILE),0)
  def value(dx,dy):return elevation.get((px+dx,py+dy),local)
  height=(value(0,0)*(1-fx)+value(1,0)*fx)*(1-fy)+(value(0,1)*(1-fx)+value(1,1)*fx)*fy
  height+=(coarse(x,y,52)-.35)*15+(coarse(x+483,y+127,27)-.42)*6
  row.append(height)
 field.append(row)
def pick_colors(a,b,step):
 return bytes(round(x+(y-x)*step) for x,y in zip(a,b))
rock={
 'meadow':rgb('8c7d56'),'rainforest':rgb('57654b'),'wetland':rgb('746c52'),
 'alpine':rgb('748493'),'tundra':rgb('879695'),'volcanic':rgb('69545d'),
 'desert':rgb('b8895b'),'steppe':rgb('a28c59'),'coast':rgb('c3aa7a')
}
dark={k:rgb(v[0]) for k,v in palette.items()}
def measure(x,y):return field[max(0,min(count-1,y))][max(0,min(count-1,x))]
bank_colors={
 'meadow':('617b37','8d6b43','775538','b69557'),
 'rainforest':('3a6a3d','6f623e','4e4f36','998557'),
 'wetland':('596d42','77694d','554c38','a48c5d'),
 'steppe':('898746','a38148','7c6239','c6a362'),
 'desert':('c3a166','b88854','987140','e0b377'),
 'volcanic':('a77d67','765752','543f49','c39a79'),
 'alpine':('ced7cc','788794','536474','aebcba'),
 'tundra':('d1d5be','82908a','616f6d','b1bba9'),
 'coast':('e4ba74','ba8d52','917044','edc385')
}
bank_colors={key:tuple(rgb(tone) for tone in set_) for key,set_ in bank_colors.items()}
for y in range(SIZE):
 for x in range(SIZE):
  b=kind(x,y)
  ix,iy=x%TILE,y%TILE
  d,dx,dy=min((ix,-1,0),(TILE-1-ix,1,0),(iy,0,-1),(TILE-1-iy,0,1))
  near=terrain.get((x//TILE+dx,y//TILE+dy),'water')
  jitter=coarse(x,y,9)
  gn=noise(x,y)
  if b=='water':
   index=1+int(coarse(x,y,62)*2+coarse(x,y,22)*1.4)
   if near!='water' and d<5+jitter*3:
    index=5 if d<2+jitter*2 else 4
   elif (int(y+coarse(x,y,46)*17)%12==0 and coarse(x,y,9)>.57):
    index=max(index,4)
   c=colors[b][min(6,index)]
  elif near=='water' and d<2+jitter*4:
   c=colors['coast'][3+int(gn>.7)]
  else:
   if near!=b and near!='water' and d<4+jitter*7 and noise(x//2,y//2)<.75-d*.056:b=near
   sx,sy=x//spacing,y//spacing
   h=field[sy][sx]
   before=measure(sx-2,sy-2);after=measure(sx+2,sy+2)
   # Tilting the sampling plane gives the elevation bands visible south-facing walls.
   band_size=15 if b in ('meadow','wetland','rainforest','coast','steppe') else 20
   band=int(h//band_size)
   delta=after-before
   warmth=coarse(x,y,47)
   index=round(2.8+warmth*1.6+(1 if b=='meadow' else 0)+max(-1.45,min(1.1,delta*.16))+(gn-.5)*.6)
   c=colors[b][max(0,min(6,index))]
   wall_length=5 if b in ('alpine','tundra','volcanic') else 4
   ledge=measure(sx,sy-wall_length)
   # Do not paint a cliff through a shoreline or make traversable water read as land.
   if ledge-h>3.2 and int(ledge//band_size)>band and h>=6 and (near!='water' or d>4):
    depth=1
    while depth<wall_length and int(measure(sx,sy-depth)//band_size)<=band:depth+=1
    lip,face,foot,detail=bank_colors[b]
    if depth==1:c=lip
    elif depth==wall_length:c=pick_colors(c,foot,.75)
    else:
     c=pick_colors(face,foot,depth*.135)
     if noise(x//3,y//2)>.69 and (x+y*3)%7<4:c=pick_colors(c,detail,.43)
     if gn<.14:c=pick_colors(c,foot,.36)
   elif h>9 and int(measure(sx,sy+2)//band_size)<band and h-measure(sx,sy+2)>2.8:
    lip,_,_,detail=bank_colors[b]
    c=pick_colors(lip,detail,.31 if h%band_size<1.0 else .16)
   elif b in ('meadow','steppe','rainforest') and 0.4<h%band_size<1.15 and abs(delta)>1:
    c=pick_colors(c,colors[b][-1],.25)
  rows[y][x*3:x*3+3]=c
def tree(x,y,h,style):
 colorsets={
  'pine':('324e45','3d694d','54865a','7fa666'),
  'broad':('2e5041','416f48','57854b','79a452'),
  'tropical':('244a40','326748','4c8150','71a155'),
  'snow':('4e6568','647e7c','8da69d','c9d7c7'),
 }
 shade,base,light,lighter=colorsets[style]
 rect(x-1,y-3,2,5,'795942')
 rect(x-4,y+1,13,2,shade)
 if style in ('pine','snow'):
  for k in (0,3,6):
   top=y-h+k
   width=3+k//2
   poly([(x,top),(x-width,top+9),(x+width,top+9)],shade)
   poly([(x,top+1),(x-width+1,top+8),(x+1,top+8)],light)
   rect(x-2,top+6,3,1,lighter)
 else:
  top=y-h
  poly([(x-7,top+5),(x-4,top+1),(x+1,top),(x+6,top+3),(x+8,top+8),(x+5,top+12),(x-5,top+12),(x-8,top+9)],shade)
  poly([(x-6,top+5),(x-3,top+2),(x+1,top+1),(x+5,top+4),(x+6,top+7),(x+2,top+10),(x-5,top+9)],base)
  rect(x-4,top+4,5,2,light);rect(x-3,top+3,2,1,lighter)
  rect(x+2,top+7,3,1,light)
def ridge(x,y,w,h,volcanic=False):
 peak=x+w//3
 shadow='615159' if volcanic else '546775'
 face='a37a6c' if volcanic else '9eafb2'
 lit='bf9381' if volcanic else 'c3cfca'
 cap='d59168' if volcanic else 'e7eadd'
 poly([(x-2,y-2),(peak,y-h),(x+w,y-1),(x+w+2,y+1),(x,y+2)],shadow)
 poly([(x,y-2),(peak,y-h+1),(peak+3,y-3),(x+1,y)],face)
 poly([(x+3,y-4),(peak-1,y-h+4),(peak,y-5),(x+6,y-4)],lit)
 poly([(peak-4,y-h+7),(peak,y-h),(peak+6,y-h+8),(peak+2,y-h+6),(peak-1,y-h+9)],cap)
 rect(x+2,y-3,4,1,lit)
def grass(x,y,c):
 rect(x,y,5,1,c);rect(x+2,y-2,1,3,c);rect(x+4,y-1,1,1,c)
for tile in sorted(island,key=lambda v:(v['y'],v['x'])):
 i,b=tile['id'],tile['biome']
 x,y=tile['x']*TILE,tile['y']*TILE
 rng=random.Random(i*971+117)
 if b=='water':continue
 if b=='wetland' and rng.random()<.61:
  at=x+rng.randrange(3,13)
  poly([(at,y+23),(at+10,y+21),(at+20,y+24),(at+17,y+29),(at+3,y+28)],'527c7d')
  rect(at+2,y+25,13,2,'5e9391');rect(at+6,y+24,8,1,'9bb9a1')
 if b in ('desert','coast','steppe'):
  for k in range(2):
   xx=x+rng.randrange(3,15);yy=y+rng.randrange(8,25)
   poly([(xx,yy+2),(xx+6,yy-1),(xx+14,yy),(xx+16,yy+2),(xx+5,yy+1)],'edc88a' if b!='steppe' else 'd0bd78')
   rect(xx+4,yy+3,10,1,'b08c59')
 for _ in range(rng.randrange(3,8)):
  xx=x+rng.randrange(3,29);yy=y+rng.randrange(5,30)
  if b in ('meadow','steppe','rainforest','wetland') and rng.random()<.58:
   grass(xx,yy,'62864d' if b in ('meadow','steppe') else '3c6c4d')
   if rng.random()<.29:rect(xx+2,yy-3,2,1,rng.choice(['e7d395','d4938a','dcd8a6']))
  else:
   rect(xx,yy,3,1,'7d7b6e' if b!='desert' else 'c19b68')
   rect(xx+1,yy-1,2,1,'b2ac91' if b!='desert' else 'e2b77d')
def chunk(tag,data):return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',SIZE,SIZE,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+row for row in rows),9))+chunk(b'IEND',b'')
Path('art-build/terrain-atlas.png').write_bytes(png)
