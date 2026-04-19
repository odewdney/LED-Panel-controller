import colorsys
import re

def err(s):
    print("Error: "+s) 

colourTypes={}
def colourType(name):
    def func(cls):
        colourTypes[name]=cls
        return cls
    return func

class Colour:
    [staticmethod]
    def _convertValue(x,mn=0,mx=255):
        if isinstance(x,int):
            pass
        elif isinstance(x,float):
            pass
        elif isinstance(x,str):
            if x.endswith("%"):
                x=float(x[:-1])*mx/100
            elif x.endswith("deg"):
                x=float(x[:-3])*mx/360
            else:
                x=float(x)
        elif x is None:
            return None
        else:
            print("uknown type:"+str(type(x)))
            return None
        if x<mn: return mn
        if x>mx: return mx
        return x
    
    def toRGB(self):
        pass
    def toHslColour(self):
        if isinstance(self,HslColour): return self
        r,g,b=self.toRGB()
        h,l,s=colorsys.rgb_to_hls(r/255,g/255,b/255)
        return HslColour(h*360,s*100,l*100)

@colourType("rgb")
class RgbColour(Colour):
    def __init__(self,r,g,b):
        self.r=r
        self.g=g
        self.b=b
    @staticmethod
    def parse(r,g,b):
        r=Colour._convertValue(r)
        g=Colour._convertValue(g)
        b=Colour._convertValue(b)
        return RgbColour(r,g,b)
    def toRGB(self):
        return (self.r,self.g,self.b)
    def __repr__(self):
        return f"rgb({self.r} {self.g} {self.b})"

@colourType("hsl")
class HslColour(Colour):
    def __init__(self,h,s,l):
        self.h=h
        self.s=s
        self.l=l
    @staticmethod
    def parse(h,s,l):
        h=Colour._convertValue(h,mx=360)
        s=Colour._convertValue(s,mx=100)
        l=Colour._convertValue(l,mx=100)
        return HslColour(h,s,l)
    def toRGB(self):
        rgb = colorsys.hls_to_rgb(self.h/360,self.l/100,self.s/100)
        return (rgb[0]*255,rgb[1]*255,rgb[2]*255)
    def __repr__(self):
        return f"hsl({self.h} {self.s} {self.l})"
    
colour_match = re.compile("^(([a-z]+)|(#[\da-f][\da-f][\da-f](?:[\da-f][\da-f][\da-f])?)|((rgb|hsl)\((\d+(?:.\d*)?(?:%|deg)? \d+(?:.\d*)?%? \d+(?:.\d*)?%?)\)))$")

colour_names={
    "black":"#000000","silver":"#c0c0c0","gray":"#808080","white":"#ffffff",
    "maroon":"#800000","red":"#ff0000","purple":"#800080","fuchsia":"#ff00ff",
    "green":"#008000","lime":"#00ff00","olive":"#808000","yellow":"#ffff00",
    "navy":"#000080","blue":"#0000ff","teal":"#008080","aqua":"#00ffff"
    }
    
def GetColour(json):
    clr=json.get("colour")
    if not clr: err("no clr"); return None
    return parseColour(clr)

def parseColour(clr):
    m = colour_match.match(clr)
    if not m: err("no clr match"); return None
    c=m.group(0)
    # must be named
    if not c.startswith("#") and m.group(2):
        c=colour_names.get(c)
        if not c: err("no clr name"); return None
    if c.startswith("#"):
        c=c[1:]
        if len(c)==3:
            c=c[0]+"0"+c[1]+"0"+c[2]+"0"
        c=bytes.fromhex(c)
        return RgbColour(c[0],c[1],c[2])
    # must be func
    c=m.group(6).split()
    clrT = colourTypes.get(m.group(5))
    if not clrT: err("no clr type"); return None
    return clrT.parse(c[0],c[1],c[2])
