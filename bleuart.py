import bluetooth
import asyncio
from micropython import const
import aioble
from primitives import Queue

_ADV_INTERVAL_US = 250_000

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
#    bluetooth.FLAG_NOTIFY,

_UART_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
#    bluetooth.FLAG_WRITE,

#_UART_SERVICE = (_UART_UUID,(_UART_TX, _UART_RX),)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

_MP_STREAM_POLL = const(3)
_MP_STREAM_POLL_RD = const(0x0001)

# async
class BLEUARTStream:#(io.IOBase):
    def __init__(self,con,txchar,rxchar,extra=None):
        self.con=con
        self.txchar=txchar
        self.rxchar=rxchar
        self.extra=extra
        self.txqueue=Queue()
        self.txtask=asyncio.create_task(self.txtask())
        self.txclose=None
        self.rxqueue=Queue()
        self.rxbuf=None
    def get_extra_info(self,name,default=None):
        return self.extra[name] if self.extra and name in self.extra else default
    async def txtask(self):
        while True:
            data=await self.txqueue.get()
            if data is None: break
            if self.con.is_connected():
                self.txchar.notify(self.con,data)
            else:
                if self.txclose is None:
                    self.txclose=False
            self.txqueue.task_done()
        self.txqueue.task_done()
            
    def write(self,data):
        if self.txclose is not None: raise Exception("closed")
        if data is not None: self.txqueue.put_nowait(data)
    def writelines(self,data):
        for line in data:
            self.write(line)
            self.write(b'\n')
    async def drain(self):
        while not self.txqueue.empty():
            await self.txqueue.join()
    def close(self):
        if self.txclose is True: raise Exception("already closed")
        self.txclose=True
        self.txqueue.put_nowait(None)
    def is_closing(self):
        return self.txclose is True
    async def wait_closed(self):
        if self.txclose is not True: self.close()
        self.txqueue.join()

    async def read(self,sz=-1):
        if sz==0: return b''
        if self.rxbuf is None:
            self.rxbuf=await self.rxqueue.get()
            if self.rxbuf is None:
                self.rxbuf=False
        if not isinstance(self.rxbuf,bytes): return b''
        if sz<0 or len(self.rxbuf)<=sz:
            ret=self.rxbuf
            self.rxbuf=None
        else:
            ret=self.rxbuf[:sz]
            self.rxbuf=self.rxbuf[sz:]
        return ret
    async def readline(self):
        if isinstance(self.rxbuf,bool): return b''
        return await self.readuntil(partial=True)
    async def readuntil(self,separator=b'\n',partial=False):
        ret=b""
        while True:
            c=await self.read(1)
            if c==b'':
                if partial:
                    return ret
                raise Exception("incomplete read")
            ret+=c
            if ret.endswith(separator):
                return ret
    async def readexactly(self,n):
        ret=""
        while n>0:
            buf=await self.read(n)
            if buf==b'': raise Exception("incomplete read")
            ret+=buf
            n-=len(buf)
        return ret
            
    def feed_eof(self):
        if self.rxbuf is not False: raise Exception("not at eof")
        self.rxbuf=True
    def at_eof(self):
        return self.rxbuf==True

    async def written(self,data):
        await self.rxqueue.put(data)

class BLEUART:
    def __init__(self, ble, streamProc, name="mpy-uart", rxbuf=100):
        self._ble = ble
        self.proc=streamProc
        self.name=name
        self._ble.config(gap_name=name)
        self.service=aioble.Service(_UART_UUID)
        self.txchar = aioble.Characteristic(self.service, _UART_TX_UUID, notify=True)
        self.rxchar = aioble.BufferedCharacteristic(self.service, _UART_RX_UUID, write=True, capture=True, max_len=rxbuf, append=True)
        aioble.register_services(self.service)
        asyncio.create_task(self.written_task())
        self.conns={}
        
    async def written_task(self):
        while True:
            data = await self.rxchar.written()
            con=self.conns.get(data[0])
            if con:
                await con.written(data[1])
            else:
                print(f"data:{data}")

    async def peripheral_task(self):
        while True:
            async with await aioble.advertise(
                _ADV_INTERVAL_US,
                name=self.name,
                services=[_UART_UUID],
                appearance=_ADV_APPEARANCE_GENERIC_COMPUTER,
            ) as connection:
                print("Connection from", connection.device)
                stream=BLEUARTStream(connection,self.txchar,self.rxchar)
                self.conns[connection]=stream
                self.proc(stream)
                await connection.disconnected(timeout_ms=None)
                await stream.written(None)
                print("disconnected")
                del self.conns[connection]

if __name__ == '__main__':
    def myStreamProc(stream):
        async def w():
            cnt=1
            while True:
                stream.write(f"t={cnt}\n")
                cnt+=1
                await asyncio.sleep(1)
        async def r(t):
            while True:
                d=await stream.readline()
                #d=await stream.read(1)
                #print(f"c={d}")
                if d is None or d==b'': break
                stream.write(f"echo {d}")
            t.cancel()
                
        wt=asyncio.create_task(w())
        asyncio.create_task(r(wt))
        
    async def main():
        #t1 = asyncio.create_task(sensor_task())
        ble=bluetooth.BLE()
        b=BLEUART(ble,myStreamProc)
        t2 = asyncio.create_task(b.peripheral_task())
        #await asyncio.gather(t1, t2)
        await t2

    asyncio.run(main())

