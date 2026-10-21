import asyncio
import logging
from asyncua import Server
import threading
import sys

# Globale noder så vores tråde kan dele dem uden problemer
keyswitch_node = None
crc_node = None
SAFE_CRC = "A4F8B2C9"
HACKED_CRC = "DEADBEEF"

async def run_opc_server():
    """Kører selve OPC UA-serveren i baggrunden helt uforstyrret"""
    global keyswitch_node, crc_node
    
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840")
    server.set_server_name("Smart Factory 4.0 - Virtual Safety PLC")

    uri = "http://cybersecurity.dk"
    idx = await server.register_namespace(uri)
    plc_obj = await server.nodes.objects.add_object(idx, "Safety_System")
    
    keyswitch_node = await plc_obj.add_variable(idx, "Keyswitch_Status", "RUN")
    crc_node = await plc_obj.add_variable(idx, "Program_CRC", SAFE_CRC)
    
    await keyswitch_node.set_writable()
    await crc_node.set_writable()

    print("🤖 VIRTUEL SAFETY PLC ER STARTET PÅ opc.tcp://127.0.0.1:4840")
    print("-------------------------------------------------------------")

    async with server:
        while True:
            await asyncio.sleep(1)

def start_server_thread():
    """Hjælpefunktion til at starte den asynkrone server i en baggrundstråd"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_opc_server())

def update_node_sync(node, value):
    """Opdaterer en OPC UA-node synkront fra vores menu-tråd"""
    if node is not None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(node.write_value(value))

def console_menu():
    """Den rolige menu der kører i forgrunden uden at hoppe eller blinke"""
    # Vent lige et øjeblik på at serveren starter op og printer sin startbesked
    import time
    time.sleep(1.0)
    
    while True:
        print("\n--- VIRTUEL PLC KONTROLPANEL (Underviser-menu) ---")
        print(" [1] SIKKER TILSTAND (Alt er OK)")
        print(" [2] CYBERANGREB: Manipuler PLC-program (Ændr CRC-hash)")
        print(" [3] SÅRBARHED: Efterlad Keyswitch i 'PROGRAM' mode")
        print(" [4] Luk simulatoren")
        print("--------------------------------------------------")
        
        valg = input("Vælg et scenarie (1-4): ").strip()

        if valg == "1":
            update_node_sync(keyswitch_node, "RUN")
            update_node_sync(crc_node, SAFE_CRC)
            print("\n🟢 SYSTEM MEDDELELSE: PLC sat til SIKKER TILSTAND.")
        elif valg == "2":
            update_node_sync(crc_node, HACKED_CRC)
            print("\n🚨 SYSTEM MEDDELELSE: MALWARE SIMULERET! (CRC ændret til DEADBEEF)")
        elif valg == "3":
            update_node_sync(keyswitch_node, "PROGRAM")
            print("\n⚠️ SYSTEM MEDDELELSE: SÅRBARHED AKTIVERET (Keyswitch i PROGRAM mode)")
        elif valg == "4":
            print("\nSlukker simulatoren...")
            sys.exit(0)
        else:
            print("\nUgyldigt valg, prøv igen (Tast 1, 2, 3 eller 4).")

if __name__ == "__main__":
    # Skjul unødvendige netværkslogfiler
    logging.getLogger("asyncua").setLevel(logging.WARNING)
    
    # 1. Start OPC UA-serveren i baggrunden
    t = threading.Thread(target=start_server_thread, daemon=True)
    t.start()
    
    # 2. Start den stabile menu i forgrunden
    try:
        console_menu()
    except KeyboardInterrupt:
        print("\nSlukker simulatoren...")
