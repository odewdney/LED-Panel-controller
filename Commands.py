import asyncio
import time
from Colours import GetColour
from Gradient import GetGradient
from ColourStop import GetStops
from Panel import GetPanel,GetPanels,fillPanel

def err(s):
    print("Error: "+s)

cmds={}
def cmd(name):
    def func(f):
       cmds[name]=f
       return f
    return func

@cmd("colour")
@cmd("color")
def processColourCmd(cmd):
    clr = GetColour(cmd)
    ps=GetPanels(cmd)
    if not clr or not ps: return
    for p in ps:
        fillPanel(p, clr)
        p.clr=clr

@cmd("grad")
def processGrad(cmd):
    p = GetPanel(cmd)
    aspect = p.aspect
    stops = GetStops(cmd)
    grad=GetGradient(cmd, aspect)
    h = p.height()
    my = 1 / (h - 1) if h > 1 else 0
    for y in range(h):
        ny = y * my
        npx = p[y]
        w = len(npx)
        mx = aspect / (w - 1) if w > 1 else 0
        grad.setY(ny)
        for x in range(w):
            l = grad.getX(x * mx)
            clr = stops(l)
            rgb = p.gamma(clr)
            rgb = (rgb[0]//256, rgb[1]//256, rgb[2]//256)
            npx[x] = rgb
    p.write()
    
@cmd("fade")
def processFadeCmd(cmd):
    t=cmd["time"]
    stops=GetStops(cmd)
    ps=GetPanels(cmd)
    if not ps: return
    async def doFade(p,t,stops):
        start=time.ticks_ms()
        if stops.isSingle():
            stops=stops.clone()
            stops.addStart(p.clr)
        await asyncio.sleep(0)
        t*=1000
        end=time.ticks_add(start,t)
        while True:
            now=time.ticks_ms()
            remain=time.ticks_diff(end,now)
            if remain<=0: break
            fillPanel(p,stops((now-start)/t))
            await asyncio.sleep_ms(remain if remain<10 else 10)
        clr=stops(1)
        fillPanel(p,clr)
        p.clr=clr
    for p in ps:
        asyncio.create_task(doFade(p,t,stops))
# {"cmd":"fade","time":10,"inter":"hsl","via":"longer","stops":[{"colour":"navy"},{"colour":"maroon"}]}
# {"cmd":"fade","panel":"a","time":10,"inter":"rgb","stops":[{"colour":"blue"},{"colour":"red"}]}

def GetCommand(cmd):
    return cmds.get(cmd)
