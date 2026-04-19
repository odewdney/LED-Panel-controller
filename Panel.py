import re

ed_state=1
def ed():
    global ed_state
    x=(ed_state ^ (ed_state>>4) ^ (ed_state>>9))&1
    ed_state = ((ed_state>>1) | (x << 9))
    return ed_state & 255

dither=[0xe0,0xa0,0x20,0x40,0x60,0x80,0xc0,0x0]
def ed1(x,y):
    z=(x&3) | ((y&1)<<2)
    return dither[z]

dither2=[7,4,6,3,1,5,8,2,9]
def ed2(x,y):
    z=(x%3) + ((y%3)*3)
    return int(dither2[z]*25)


panels={}

def AddPanel(name,panel):
    panels[name]=panel

def GetPanel(cmd):
    p=cmd.get("panel")
    if p is None: return panels.get("main")
    return panels.get(p)

def GetPanels(cmd):
    p=cmd.get("panel")
    if p is not None:
        return [panels.get(p)]
    p=cmd.get("panels")
    if p is not None:
        if isinstance(p,str):
            pm = re.compile(p)
            return [x[1] for x in panels.items() if pm.search(x[0])]
        if isinstance(p,list):
            return [x[1] for x in panels.items() if x[0] in p]
        return None
    return panels.values()

def fillPanel(p,clr):
    rgb=p.gamma(clr)
    rgb2=(rgb[0]>>8,rgb[1]>>8,rgb[2]>>8)
    if (rgb[0] > 1024 or rgb[0]<1) and (rgb[1] > 1024 or rgb[1]<1) and (rgb[2] > 1024 or rgb[2]<1):
        p.fill(rgb2)
    else:
        #print(f"{type(p)} {rgb} {rgb2}")
        for y in range(p.height()):
            for x in range(p.width(y)):
                grgb=(rgb2[0] if rgb[0]>1024 else (rgb[0]+ed2(x,y))//256,
                      rgb2[1] if rgb[1]>1024 else (rgb[1]+ed2(x,y))//256,
                      rgb2[2] if rgb[2]>1024 else (rgb[2]+ed2(x,y))//256)
                #print(f"{x} {y} {grgb}")
                p[y][x]=grgb
    p.write()
