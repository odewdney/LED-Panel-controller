import time
from Commands import cmd,GetCommand
#from NeoPanel import NeoPanel
from Panel import AddPanel,GetPanel, loadPanel
from Colours import parseColour
#import neopixel
#import machine
import sys
import asyncio
import json

def err(s):
    print(s)
    
@cmd("size")
def processSizeCmd(cmd):
    pass

line=""
async def readCmd(stm):
    global line
    while True:
        line = await stm.readline()
        if line==b'': break
        while line.endswith(b'\n') or line.endswith(b'\r'):
            line=line[:-1]
        if len(line)==0: continue
        try:
            if line.startswith('{') or line.startswith("["):
                line = json.loads(line)
            else:
                line={"cmd":"colour","colour":line.decode(),"panels":"."}
            #print(f"line:{line}")
        except Exception as e:
            err(f"not json:{line} {e}")
            continue
        if isinstance(line,dict):
            line = [line]
        if isinstance(line,list):
            for entry in line:
                cmd=entry.get("cmd")
                if not cmd: err("no cmd"); continue
                c=GetCommand(cmd)
                if not c: err("not cmd"); continue
                c(entry)
        else:
            print(f"line is:{type(line)}")
                


with open("leds.json",'r') as f:
    cfg = json.load(f)
    loadPanel(cfg)

#p=machine.Pin(16) # 21 - onboard led, 16-esp32-s2 13-esp32-s3
#np=neopixel.NeoPixel(p,256)
#demo(np)

#npa=np.GetSlice(0,9)
#npb=np.GetSlice(128,255)

#np.fill((0,0,0))
#np.write()
#time.sleep(0.1)

#nps=NeoPanel(npa,1,[(0,2),(5,3),(6,8)])
#nps=NeoPanel(npa,0.5,[(x*8+7 if x & 1 else x*8,x*8 if x & 1 else x*8+7)   for x in range(16)])
#npb=NeoPanel(npb,0.5,[(x*8+7 if x & 1 else x*8,x*8 if x & 1 else x*8+7)   for x in range(16)])

#AddPanel("main",nps)
#AddPanel("r",npb)

#nps[0].fill((1,0,0))
#nps[1].fill((0,1,0))
#nps[2].fill((0,0,1))
#np.write()

stm = asyncio.StreamReader(sys.stdin)
t=asyncio.create_task(readCmd(stm))

import bleuart
import bluetooth

def bleproc(stm):
    asyncio.create_task(readCmd(stm))
ble=bluetooth.BLE()
b=bleuart.BLEUART(ble,bleproc)
t2 = asyncio.create_task(b.peripheral_task())


t=asyncio.run_until_complete(t)

