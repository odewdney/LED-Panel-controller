import neopixel

gamma = [int(((i/256) ** 2.8) * 65536) for i in range(256)]
def rgb_to_led(clr):
    rgb=clr.toRGB()
    return (gamma[int(rgb[0])],gamma[int(rgb[1])],gamma[int(rgb[2])])

neopixel.NeoPixel.__len__ = lambda self : self.n

#NeoPixel_getitem_orig=neopixel.NeoPixel.__getitem__
#def NewPixel_getitem(self,index):
#    if isinstance(index,slice):
#        return NeoSlice(self,slice)
#    return NeoPixel_getitem_orig(self,index)
#neopixel.NeoPixel.__getitem__=NewPixel_getitem

class NeoSlice:
    def __init__(self,px,start,end,reversed):
        self.px=px
        self.start=start
        self.end=end
        self.rev=reversed
    def getIndex(self,index):
        if self.rev:
            return self.end-index
        return index+self.start
    def __len__(self):
        return 1+self.end-self.start
    def __setitem__(self,index,val):
        self.px[self.getIndex(index)]=val
    def __getitem__(self,index):
        return self.px[self.getIndex(index)]
    def fill(self,val):
        for i in range(self.start,self.end+1):
            self.px[i]=val
    def GetSlice(self,start,end,rev=False):
        return NeoSlice(self.px,self.start+start,self.start+end,rev)
    def write(self):
        self.px.write()
    def _repr__(self):
        return f"NeoSlice({self.p},{self.start},{self.end})"

def NeoPixel_Slice(self,start,end,rev=False):
    return NeoSlice(self,start,end,rev)
neopixel.NeoPixel.GetSlice=NeoPixel_Slice

class NeoPanel:
    def __init__(self,px,aspect,rows):
        self.px=px
        self.aspect=aspect
        self.rows=[]
        for row in rows:
            s=row[0]
            e=row[1]
            self.rows.append(px.GetSlice(s,e) if s<=e else px.GetSlice(e,s,True))
    def height(self):
        return len(self.rows)
    def width(self,row):
        return len(self.rows[row])
    def __setitem__(self,index,c):
        self.rows[index[1]][index[0]]=c
    def __getitem__(self,index):
        return self.rows[index]
    def fill(self,clr):
        for row in self.rows:
            row.fill(clr)
    def write(self):
        self.px.write()
    def gamma(self,clr):
        return rgb_to_led(clr)
    def __repr__(self):
        return f"NeoPanel({self.aspect},{self.width(0)},{self.height()})"
