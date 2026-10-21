import asyncio
from asyncua import Client

KNOWN_GOOD_CRC = "A4F8B2C9"

class PLCNetworkClient:
    def __init__(self):
        self.live_key = "OFFLINE"
        self.live_crc = "OFFLINE"
        self.url = "opc.tcp://127.0.0.1:4840"

    async def poll_loop(self):
        """Konstant baggrundsscanning af simulatoren via port 4840"""
        while True:
            try:
                async with Client(url=self.url, timeout=1) as client:
                    key_node = client.get_node("ns=2;i=2")
                    crc_node = client.get_node("ns=2;i=3")
                    self.live_key = await key_node.read_value()
                    self.live_crc = await crc_node.read_value()
            except:
                self.live_key = "OFFLINE"
                self.live_crc = "OFFLINE"
            await asyncio.sleep(0.3)

    async def send_recovery(self):
        """Sender et trådløst rensningssignal retur til simulatoren"""
        try:
            async with Client(url=self.url, timeout=2) as client:
                key_node = client.get_node("ns=2;i=2")
                crc_node = client.get_node("ns=2;i=3")
                await key_node.write_value("RUN")
                await crc_node.write_value(KNOWN_GOOD_CRC)
            return True
        except:
            return False
