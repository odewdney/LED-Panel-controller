from Colours import *

def lerp(s,e,f):
    return s+(e-s)*f

def GetFadeRgb(cmd):
    def fadeRgb(c1,c2,f):
        rgb1=c1.toRGB()
        rgb2=c2.toRGB()
        return RgbColour(lerp(rgb1[0],rgb2[0],f),lerp(rgb1[1],rgb2[1],f),lerp(rgb1[2],rgb2[2],f))
    return fadeRgb

def GetFadeHsl(cmd):
    via=cmd.get("via")
    
    if via is None or via=="shorter":
        viaFunc = lambda h1,h2: (h1,h2) if abs(h1-h2)<180 else (h1+360,h2) if h1<h2 else (h1,h2+360)
    elif via=="longer":
        viaFunc = lambda h1,h2: (h1,h2) if abs(h1-h2)>180 else (h1+360,h2) if h1<h2 else (h1,h2+360)
    elif via=="increasing":
        viaFunc = lambda h1,h2: (h1, h2 if h2>h1 else h2+360)
    elif via=="decreasing":
        viaFunc = lambda h1,h2: (h1 if h2>h1 else h1+360, h2)
    else:
        raise "unknown via"
    def fadeHsl(c1,c2,f):
        hsl1=c1.toHslColour()
        hsl2=c2.toHslColour()
        h1=hsl1.h
        h2=hsl2.h
        h1,h2=viaFunc(h1,h2)
        h=lerp(h1,h2,f)%360
        return HslColour(h,lerp(hsl1.s,hsl2.s,f),lerp(hsl1.l,hsl2.l,f))
    return fadeHsl

def GetFadeFunc(cmd):
    i=cmd.get("inter")
    if i is None or i=="rgb":
        fadeFunc=GetFadeRgb(cmd)
    elif i=="hsl":
        fadeFunc=GetFadeHsl(cmd)
    else:
        raise "unknown fade"
    return fadeFunc
