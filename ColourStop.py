from Colours import GetColour, parseColour
from GetFadeFunc import GetFadeFunc

class ColourStop:
    def __init__(self,clr,pos):
        self.clr=clr
        self.setPos(pos)
    def setPos(self,pos):
        self.pos=pos
        if isinstance(pos,list):
            self.start=pos[0]/100
            self.end=pos[1]/100
        elif pos is not None:
            self.start=self.end=pos/100
        else:
            self.start=self.end=None
    def __repr__(self):
        return f"stop({self.clr},{self.start},{self.end})"

def GetStops(cmd):
    stops=cmd["stops"]
    ret=[]
    for stop in stops:
        if isinstance(stop,dict):
            clr=GetColour(stop)
            pos=stop.get("pos")
        elif isinstance(stop,str):
            clr=parseColour(stop)
            pos=None
        else:
            return None
        if clr is None: return None
        ret.append(ColourStop(clr,pos))
    if len(ret)==0: return None
    if ret[0].start is None: ret[0].setPos(0)
    if ret[-1].start is None: ret[-1].setPos(100)
    def getEndPosStop(n):
        for x in range(n+1,len(ret)):
            if ret[x].start is not None: return x
    for n in range(1,len(ret)-1):
        if ret[n].pos is None:
            s=ret[n-1].end
            es=getEndPosStop(n)
            e=ret[es].start
            ret[n].setPos(100*(e-s)/(es-n+1))
    fadeFunc=GetFadeFunc(cmd)
    def getColour(f):
        for n in range(len(ret)):
            rr=ret[n]
            if f<=rr.end:
                if n==0 or f>=rr.start:
                    return rr.clr
                pr=ret[n-1]
                s=pr.end
                e=rr.start
                ff=(f-s)/(e-s)
                return fadeFunc(pr.clr,rr.clr,ff)
        return ret[-1].clr
    return getColour
