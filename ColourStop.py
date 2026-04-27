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

class ColourStops:
    def __init__(self,stops,fadeFunc):
        self.stops=stops
        self.fadeFunc=fadeFunc
        self.init=False
    def __repr__(self):
        return [s for s in self.stops]

    def getEndPosStop(self,n):
        for x in range(n+1,len(self.stops)):
            if self.stops[x].start is not None: return x
    def initialise(self):
        stops=self.stops
        if stops[0].start is None: stops[0].setPos(0)
        if stops[-1].start is None: stops[-1].setPos(100)
        for n in range(1,len(stops)-1):
            if stops[n].pos is None:
                s=stops[n-1].end
                es=self.getEndPosStop(n)
                e=stops[es].start
                stops[n].setPos(100*(e-s)/(es-n+1))
        self.init=True

    def __call__(self,f):
        if not self.init: self.initialise()
        for n in range(len(self.stops)):
            rr=self.stops[n]
            if f<=rr.end:
                if n==0 or f>=rr.start:
                    return rr.clr
                pr=self.stops[n-1]
                s=pr.end
                e=rr.start
                ff=(f-s)/(e-s)
                return self.fadeFunc(pr.clr,rr.clr,ff)
        return self.stops[-1].clr
    def isSingle(self):
        return len(self.stops)==1
    def clone(self):
        return ColourStops(self.stops[:],self.fadeFunc)
    def addStart(self,clr):
        self.stops.insert(0,ColourStop(clr,0))

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
    fadeFunc=GetFadeFunc(cmd)
    return ColourStops(ret,fadeFunc)

# test
if __name__ == '__main__':
    s=GetStops({"stops":["red",{"colour":"green","pos":10},"blue"]})
    s=s.clone()
    s.addStart(parseColour("red"))
