"""Terminal engine with authentic tshark CLI protocol dissector, filtering & auto-complete."""

from __future__ import annotations

import re
import shlex
from typing import Any


class TSharkEngine:
    """Authentic industrial tshark (Wireshark CLI) network sniffer & protocol dissector."""

    def __init__(self) -> None:
        self.active_filter: str = ""

    def get_packets_for_zone(self, room: str, engine: Any = None) -> list[dict[str, Any]]:
        flags = getattr(engine, "flags", set()) if engine else set()
        scada_blind = getattr(engine, "scada_blind", False) if engine else False
        c1_done = "chapter-1-done" in flags
        c2_done = "chapter-2-done" in flags
        c3_done = "chapter-3-done" in flags
        c4_done = "chapter-4-done" in flags
        pi_removed = "pi-removed" in flags

        if room == "indgangen":
            return [
                {
                    "no": "001", "time": "0.000000", "src": "192.168.1.50", "dst": "10.20.1.20",
                    "proto": "Modbus", "func": "16", "info": "Query: Write Multiple Registers (FC 16) [TEST-SPOR: MORTENS SERVICE-LOG]",
                    "dissection": [
                        "Frame 1: 74 bytes på kablet (VLAN 40 - Enterprise/Perimeter SPAN-port)",
                        "Internet Protocol Version 4, Src: 192.168.1.50 (Hydropump Service-PC), Dst: 10.20.1.20 (Pumpe 2 VFD)",
                        "Transmission Control Protocol, Src Port: 51200, Dst Port: 502",
                        "Modbus/TCP: Function 16 (Write Multiple Registers) - Logget under gårsdagens servicebesøg",
                        " Forensisk Note: Dette spor ('spor_morten_rapport') kan nu analyseres på Sagstavlen!",
                    ],
                },
                {
                    "no": "002", "time": "0.004210", "src": "10.20.4.10", "dst": "10.20.4.1",
                    "proto": "ICMP", "func": "Echo", "info": "Echo (ping) request — Gateway Health Check (Purdue Level 4 -> IDMZ)",
                    "dissection": [
                        "Frame 2: 42 bytes på kablet (VLAN 40)",
                        "Normal perimetertjek fra Hovedindgangens test-switch.",
                    ],
                },
            ]

        if room == "pumpehuset":
            if scada_blind:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.1.5", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "3", "info": "FC 03 Read Holding Registers [BLOKERET AF FIREWALL - INGEN ALLOW-REGEL FOR FC 03!]",
                        "dissection": [
                            "Frame 1: 66 bytes på kablet (VLAN 10)",
                            "Internet Protocol Version 4, Src: 10.20.1.5 (WinCC SCADA), Dst: 10.20.1.20 (VFD)",
                            "Transmission Control Protocol, Src Port: 54120, Dst Port: 502",
                            "Modbus/TCP: FC 03 Read Holding Registers | Reg: 0x0000, Len: 2",
                            "SCALANCE S615 DPI Filter: [DROP] Default-deny policy droppede pakken fordi FC 03 mangler allow-regel!",
                        ],
                    },
                    {
                        "no": "002", "time": "0.001150", "src": "10.20.1.5", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "RST", "info": "[TCP TIMEOUT / CONNECTION RESET] SCADA modtager ingen telemetri!",
                        "dissection": [
                            "Frame 2: 54 bytes på kablet (VLAN 10)",
                            "WinCC SCADA Process Telemetry: TIMEOUT - intet svar fra Pumpe 2.",
                            "Konsekvens: SCADA-operatøren ser '??? BAR' på driftsskærmen!",
                        ],
                    },
                    {
                        "no": "003", "time": "0.012540", "src": "10.20.1.77", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "6", "info": "FC 06 Write Single Register [DROPPED BY DPI RULE #1]",
                        "dissection": [
                            "Frame 3: 66 bytes på kablet (VLAN 10)",
                            "Internet Protocol Version 4, Src: 10.20.1.77 (Angriber), Dst: 10.20.1.20 (VFD)",
                            "Modbus/TCP: FC 06 Write Single Register | Reg: 0x0000, Value: 1337",
                            "SCALANCE S615 DPI Filter: [DROP & LOG] Sabotagepakke blokeret succesfuldt.",
                        ],
                    },
                ]
            elif c1_done:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.1.5", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "3", "info": "FC 03 Read Holding Registers [DPI ACCEPT: Telemetri OK]",
                        "dissection": [
                            "Frame 1: 66 bytes på kablet (VLAN 10)",
                            "Internet Protocol Version 4, Src: 10.20.1.5 (WinCC SCADA), Dst: 10.20.1.20 (VFD)",
                            "Transmission Control Protocol, Src Port: 54120, Dst Port: 502",
                            "Modbus/TCP: FC 03 Read Holding Registers | Reg: 0x0000, Len: 2",
                            "SCALANCE S615 DPI Filter: [PERMIT] FC 03 godkendt jf. whitelist regel #2.",
                        ],
                    },
                    {
                        "no": "002", "time": "0.000490", "src": "10.20.1.20", "dst": "10.20.1.5",
                        "proto": "Modbus", "func": "3", "info": "Response: FC 03 | Tryk: 42.0 Bar (Stabil drift)",
                        "dissection": [
                            "Frame 2: 70 bytes på kablet (VLAN 10)",
                            "Modbus/TCP Response: Register 0x0000 = 420 (42.0 Bar nominelt driftstryk)",
                        ],
                    },
                    {
                        "no": "003", "time": "0.012540", "src": "10.20.1.77", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "6", "info": "FC 06 Write Single Register [DROPPED BY DPI RULE #1]",
                        "dissection": [
                            "Frame 3: 66 bytes på kablet (VLAN 10)",
                            "Internet Protocol Version 4, Src: 10.20.1.77 (Angriber), Dst: 10.20.1.20 (VFD)",
                            "Modbus/TCP: FC 06 Write Single Register | Reg: 0x0000, Value: 1337",
                            "SCALANCE S615 DPI Filter: [DROP & LOG] Sabotagepakke blokeret succesfuldt.",
                        ],
                    },
                ]
            else:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.1.5", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "3", "info": "Query: Read Holding Registers (FC 03)",
                        "dissection": [
                            "Frame 1: 66 bytes på kablet (VLAN 10)",
                            "Ethernet II, Src: 00:1c:06:12:34:56 (Siemens HMI), Dst: 00:0e:8c:aa:bb:cc (SINAMICS VFD)",
                            "Internet Protocol Version 4, Src: 10.20.1.5, Dst: 10.20.1.20",
                            "Transmission Control Protocol, Src Port: 54120, Dst Port: 502",
                            "Modbus/TCP: Transaction: 0x0001 | Unit ID: 1 | Function: Read Holding Registers (3) | Reg: 0x0000, Len: 2",
                        ],
                    },
                    {
                        "no": "002", "time": "0.000490", "src": "10.20.1.20", "dst": "10.20.1.5",
                        "proto": "Modbus", "func": "3", "info": "Response: Read Holding Registers (FC 03) [146.5 Bar!]",
                        "dissection": [
                            "Frame 2: 70 bytes på kablet (VLAN 10)",
                            "Internet Protocol Version 4, Src: 10.20.1.20, Dst: 10.20.1.5",
                            "Transmission Control Protocol, Src Port: 502, Dst Port: 54120",
                            "Modbus/TCP: Transaction: 0x0001 | Function: Read Holding Registers (3) | Data: 0x0539 (1465 = 146.5 Bar)",
                        ],
                    },
                    {
                        "no": "003", "time": "0.012540", "src": "10.20.1.77", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "6", "info": "Query: Write Single Register (FC 06) [SABOTAGE REG 0x0000=1337]",
                        "dissection": [
                            "Frame 3: 66 bytes på kablet (VLAN 10)",
                            "Ethernet II, Src: dc:a6:32:99:88:77 (Ukendt MAC), Dst: 00:0e:8c:aa:bb:cc (SINAMICS VFD)",
                            "Internet Protocol Version 4, Src: 10.20.1.77, Dst: 10.20.1.20",
                            "Transmission Control Protocol, Src Port: 49152, Dst Port: 502",
                            "Modbus/TCP: Function: Write Single Register (6) | Reg: 0x0000, Value: 1337 (146.5 Bar)",
                            "ADVARSEL: Ubeskyttet Modbus TCP tillader vilkårlig registerskrivning!",
                        ],
                    },
                    {
                        "no": "004", "time": "0.012980", "src": "10.20.1.20", "dst": "10.20.1.77",
                        "proto": "Modbus", "func": "6", "info": "Response: Write Single Register (FC 06)",
                        "dissection": [
                            "Frame 4: 66 bytes på kablet (VLAN 10)",
                            "Modbus/TCP Echo Response: Register 0x0000 = 1337",
                        ],
                    },
                    {
                        "no": "005", "time": "0.024890", "src": "10.20.1.77", "dst": "10.20.1.20",
                        "proto": "Modbus", "func": "6", "info": "Query: Write Single Register (FC 06) [SABOTAGE CYKLUS]",
                        "dissection": [
                            "Frame 5: Angriberens loop fastholder det ekstreme setpunkt.",
                            "Pumpe 2 nærmer sig sprængningsgrænsen på 150 Bar!",
                        ],
                    },
                ]

        elif room == "ventil-oen":
            if c2_done:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "00:0e:8c:aa:11:01", "dst": "00:0e:8c:bb:22:02",
                        "proto": "PROFINET", "func": "RT", "info": "PROFINET Real-Time Cyclic I/O (SCALANCE MRP-Ring: Stabil)",
                        "dissection": [
                            "Frame 1: Layer 2 PROFINET RT (IEEE 802.1Q VLAN 20 Priority 6)",
                            "Managed Switch: SCALANCE XB-200 håndhæver deterministisk MRP ring redundancy.",
                            "Port Security: Aktiv (Sticky MAC).",
                        ],
                    },
                ]
            elif pi_removed:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "00:0e:8c:aa:11:01", "dst": "00:0e:8c:bb:22:02",
                        "proto": "PROFINET", "func": "RT", "info": "PROFINET Real-Time Cyclic I/O (DCP storm ophørt)",
                        "dissection": [
                            "Frame 1: Layer 2 PROFINET RT (IEEE 802.1Q VLAN 20 Priority 6)",
                            "Rogue implantat fjernet. Netværket afventer montering af managed switch.",
                        ],
                    },
                ]
            else:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "00:0e:8c:aa:11:01", "dst": "00:0e:8c:bb:22:02",
                        "proto": "PROFINET", "func": "RT", "info": "PROFINET Real-Time Cyclic I/O (Frame ID: 0x8000)",
                        "dissection": [
                            "Frame 1: Layer 2 PROFINET RT (IEEE 802.1Q VLAN 20 Priority 6)",
                            "Cycle Counter: 0x1402 | Data Status: 0x35 (Valid, Primary, Run)",
                        ],
                    },
                    {
                        "no": "002", "time": "0.000210", "src": "b8:27:eb:d4:11:22", "dst": "ff:ff:ff:ff:ff:ff",
                        "proto": "PN-DCP", "func": "Set", "info": "DCP Set: NameOfStation='rogue-io' [HIJACKING]",
                        "dissection": [
                            "Frame 2: 60 bytes på kablet (VLAN 20)",
                            "Ethernet II, Src: b8:27:eb:d4:11:22 (Raspberry Pi Foundation), Dst: ff:ff:ff:ff:ff:ff",
                            "PROFINET DCP (Discovery & Basic Configuration Protocol)",
                            "Service ID: Set (0x04) | Service Type: Request (0x00)",
                            "Block: Device Properties / NameOfStation = 'rogue-io'",
                        ],
                    },
                    {
                        "no": "003", "time": "0.000450", "src": "b8:27:eb:d4:11:22", "dst": "00:0e:8c:aa:11:01",
                        "proto": "ARP", "func": "Spoof", "info": "ARP Reply: 10.20.2.50 is at b8:27:eb:d4:11:22 [ARP POISONING]",
                        "dissection": [
                            "Frame 3: ARP Cache Poisoning mod PLC og ventil-ø.",
                            "Angriberens Raspberry Pi leder felttrafik igennem sig som Man-in-the-Middle.",
                        ],
                    },
                    {
                        "no": "004", "time": "0.000890", "src": "b8:27:eb:d4:11:22", "dst": "ff:ff:ff:ff:ff:ff",
                        "proto": "PN-DCP", "func": "Identify", "info": "DCP Identify Request Broadcast Storm (1200 pkts/s)",
                        "dissection": [
                            "Frame 4: Layer 2 broadcast storm overloader den unmanaged D-Link switch.",
                            "ET 200SP I/O mister determinisme og ventilerne oscillerer ukontrolleret!",
                        ],
                    },
                ]

        elif room == "el-tavlen":
            if c3_done:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.3.15", "dst": "10.20.3.1",
                        "proto": "S7comm", "func": "Read", "info": "Read Variable (Protection Level 3: Godkendt HMI)",
                        "dissection": [
                            "Frame 1: Siemens S7comm på Port 102",
                            "Protection Level 3 (Read-only for HMI) håndhævet af S7-1500 CPU 1516F.",
                            "PUT/GET kommunikation er deaktiveret i hardware-konfigurationen.",
                        ],
                    },
                    {
                        "no": "002", "time": "0.001200", "src": "10.20.1.77", "dst": "10.20.3.1",
                        "proto": "S7comm", "func": "PUT", "info": "Job: Write Variable (PUT) [AFVIST: ERROR 0x8104 - ACCESS DENIED]",
                        "dissection": [
                            "Frame 2: Angriberens PUT/GET forsøg afvist af S7 CPU firmware.",
                        ],
                    },
                ]
            else:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.3.15", "dst": "10.20.3.1",
                        "proto": "COTP", "func": "CR", "info": "COTP Connection Request (TSAP: 0x0102)",
                        "dissection": [
                            "Frame 1: ISO on TCP (RFC 1006) på Port 102",
                            "COTP PDU Type: CR (Connection Request)",
                        ],
                    },
                    {
                        "no": "002", "time": "0.001200", "src": "10.20.1.77", "dst": "10.20.3.1",
                        "proto": "S7comm", "func": "PUT", "info": "Job: Write Variable (PUT to DB1.DBX0.0) [UAUTORISERET]",
                        "dissection": [
                            "Frame 2: Siemens S7 Communication på Port 102",
                            "Header: ROSCTR: Job (1) | PDU Reference: 0x0042",
                            "Function: Write Variable (0x05) | Parameter Count: 1",
                            "Data: Overskriver Safety Checksum i DB1 -> Tvinger CPU i STOP!",
                        ],
                    },
                    {
                        "no": "003", "time": "0.001850", "src": "10.20.3.1", "dst": "10.20.1.77",
                        "proto": "S7comm", "func": "Error", "info": "Ack-Data: Error Code 0x8104 (Context not supported / STOP)",
                        "dissection": [
                            "Frame 3: CPU 1516F skifter til STOP-mode.",
                        ],
                    },
                ]

        elif room == "kontrolrummet":
            if c4_done:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.4.10", "dst": "10.20.2.10",
                        "proto": "OPC.TCP", "func": "Open", "info": "OpenSecureChannel: Basic256Sha256 / SignAndEncrypt [SIKRET]",
                        "dissection": [
                            "Frame 1: OPC UA Binary Protocol på Port 4840",
                            "SecurityPolicy: http://opcfoundation.org/UA/SecurityPolicy#Basic256Sha256",
                            "MessageSecurityMode: SignAndEncrypt",
                            "X.509 Certifikat: WinCC_SCADA.der (Valideret & Trusted i serverens truststore).",
                            "UserToken: Role-based Authentication (Anonymous DISABLED).",
                        ],
                    },
                ]
            else:
                return [
                    {
                        "no": "001", "time": "0.000000", "src": "10.20.4.10", "dst": "10.20.2.10",
                        "proto": "OPC.TCP", "func": "Hello", "info": "OPC UA TCP Hello (opc.tcp://10.20.2.10:4840)",
                        "dissection": [
                            "Frame 1: OPC UA Binary Protocol på Port 4840",
                            "Message Type: HEL (Hello)",
                        ],
                    },
                    {
                        "no": "002", "time": "0.002100", "src": "10.20.4.10", "dst": "10.20.2.10",
                        "proto": "OPC.TCP", "func": "Open", "info": "OpenSecureChannel: SecurityPolicy='None' [UKRYPTERET]",
                        "dissection": [
                            "Frame 2: SecurityPolicy: http://opcfoundation.org/UA/SecurityPolicy#None",
                            "MessageSecurityMode: None (Ingen kryptering, ingen signatur!)",
                            "Konsekvens: Procesdata og opskrifter lækkes i klartekst over nettet.",
                        ],
                    },
                    {
                        "no": "003", "time": "0.003500", "src": "10.20.4.10", "dst": "10.20.2.10",
                        "proto": "OPC.TCP", "func": "Session", "info": "CreateSession: UserTokenType=Anonymous [INGEN ADGANGSKONTROL]",
                        "dissection": [
                            "Frame 3: Anonym login accepteret. Fuld adgang til doseringsopskrifter og ventilstyring!",
                        ],
                    },
                    {
                        "no": "004", "time": "0.015200", "src": "192.168.1.1", "dst": "10.20.2.10",
                        "proto": "TCP", "func": "SYN", "info": "Inbound TCP connection fra Teltonika 4G VPN tunnel [BACKDOOR]",
                        "dissection": [
                            "Frame 4: Ekstern IP (185.220.101.5) tunneleret via uautoriseret 4G-router direkte ind i IDMZ!",
                        ],
                    },
                ]
        return []

    def execute_tshark_command(self, cmd_line: str, room: str, engine: Any = None) -> str:
        """Parses and executes a realistic tshark CLI command string."""
        raw = cmd_line.strip()
        tokens = raw.split()
        if not tokens:
            return self.render_tshark_capture(room, filter_str="", count=0, verbose=False, fields=[], engine=engine)

        # Help / manual requests
        if any(h in tokens for h in {"--help", "-h", "help"}) or raw in {"man tshark", "cheat tshark", "tshark cheatsheet"}:
            return self.get_tshark_manual()

        # Parse flags
        display_filter = ""
        count = 0
        verbose = "-V" in tokens
        fields: list[str] = []

        # Find display filter -Y "<filter>"
        if "-Y" in tokens:
            y_idx = tokens.index("-Y")
            if y_idx + 1 < len(tokens):
                try:
                    parsed_args = shlex.split(raw)
                    if "-Y" in parsed_args:
                        display_filter = parsed_args[parsed_args.index("-Y") + 1]
                except Exception:
                    display_filter = tokens[y_idx + 1].strip("\"'")

        # Find count -c <n>
        if "-c" in tokens:
            c_idx = tokens.index("-c")
            if c_idx + 1 < len(tokens):
                try:
                    count = int(tokens[c_idx + 1])
                except ValueError:
                    pass

        # Find fields -T fields -e <field>
        if "-T" in tokens and "fields" in tokens:
            for idx, tok in enumerate(tokens):
                if tok == "-e" and idx + 1 < len(tokens):
                    fields.append(tokens[idx + 1])

        # If user just wrote 'tshark <filter>' without -Y, be pedagogically helpful!
        if not display_filter and len(tokens) > 1 and not tokens[1].startswith("-"):
            guess_filter = tokens[1]
            return (
                f"💡 [TSHARK SYNTAKS-TIPS]: I tshark skal et display-filter angives med flaget -Y.\n"
                f"Eksempel: tshark -Y \"{guess_filter}\"\n\n"
                + self.render_tshark_capture(room, filter_str=guess_filter, count=count, verbose=verbose, fields=fields, engine=engine)
            )

        return self.render_tshark_capture(room, filter_str=display_filter, count=count, verbose=verbose, fields=fields, engine=engine)

    def render_tshark_capture(
        self,
        room: str,
        filter_str: str = "",
        count: int = 0,
        verbose: bool = False,
        fields: list[str] | None = None,
        engine: Any = None,
    ) -> str:
        packets = self.get_packets_for_zone(room, engine=engine)
        if not packets:
            return f"tshark: Ingen aktive netværksgrænseflader med trafik i zonen [{room}]."

        norm_filt = filter_str.lower().strip()
        filtered_pkts: list[dict[str, Any]] = []

        for p in packets:
            full_text = f"{p['no']} {p['time']} {p['src']} {p['dst']} {p['proto']} {p['func']} {p['info']}".lower()
            if not norm_filt:
                filtered_pkts.append(p)
            elif "modbus.func_code" in norm_filt:
                match = re.search(r"modbus\.func_code\s*==\s*(\d+)", norm_filt)
                target_fc = match.group(1) if match else ""
                if target_fc and p.get("func") == target_fc:
                    filtered_pkts.append(p)
                elif not target_fc and p["proto"].lower() == "modbus":
                    filtered_pkts.append(p)
            elif "modbus" in norm_filt and p["proto"].lower() == "modbus":
                filtered_pkts.append(p)
            elif "pn_dcp" in norm_filt and "dcp" in full_text:
                filtered_pkts.append(p)
            elif "pn_rt" in norm_filt and "profinet" in full_text:
                filtered_pkts.append(p)
            elif ("b8:27:eb" in norm_filt or "mac" in norm_filt) and ("b8:27:eb" in full_text or "rogue" in full_text):
                filtered_pkts.append(p)
            elif "s7comm" in norm_filt and ("s7" in full_text or "cotp" in full_text):
                filtered_pkts.append(p)
            elif "opcua" in norm_filt and "opc" in full_text:
                filtered_pkts.append(p)
            elif norm_filt in full_text:
                filtered_pkts.append(p)

        if count > 0:
            filtered_pkts = filtered_pkts[:count]

        # Field extraction mode (-T fields -e ...)
        if fields:
            lines = [f"# tshark -T fields -e {' -e '.join(fields)}"]
            for p in filtered_pkts:
                vals = []
                for f in fields:
                    if "ip.src" in f:
                        vals.append(p["src"])
                    elif "ip.dst" in f:
                        vals.append(p["dst"])
                    elif "proto" in f:
                        vals.append(p["proto"])
                    elif "func" in f:
                        vals.append(p.get("func", "-"))
                    else:
                        vals.append(p.get("info", "-"))
                lines.append("\t".join(vals))
            return "\n".join(lines)

        # Standard or Verbose output
        lines = [
            f"Capturing on '{room}_vlan' (tshark v4.2.0 - OT Sniffer)",
            f"Display filter: \"{filter_str}\"" if filter_str else "Display filter: <none> (capturing all)",
            "----------------------------------------------------------------------------------------",
        ]

        if not filtered_pkts:
            lines.append("  0 packets captured matching display filter.")
        elif verbose:
            for p in filtered_pkts:
                lines.append(f"\nFrame {int(p['no'])}: {len(p.get('dissection', []))} layers on wire")
                for d in p.get("dissection", []):
                    lines.append(f"    {d}")
        else:
            for p in filtered_pkts:
                lines.append(f"  {p['no']:<4} {p['time']:<9} {p['src']:<15} -> {p['dst']:<15} {p['proto']:<9} {p['info']}")

        lines.append("----------------------------------------------------------------------------------------")
        lines.append("💡 [TSHARK PRO-TIPS]:")
        lines.append("  • Filtrer specifik Modbus FC:   tshark -Y \"modbus.func_code == 6\"")
        lines.append("  • Detaljeret dissektion:        tshark -Y \"modbus\" -V")
        lines.append("  • Se fuld manual & syntaks:     man tshark  eller  cheat tshark")
        return "\n".join(lines)

    def render_capture(self, room: str, filter_str: str = "") -> str:
        """Backward-compatibility for older wireshark calls."""
        return self.execute_tshark_command(f"tshark -Y \"{filter_str}\"" if filter_str else "tshark", room)

    def render_dissection(self, room: str, pkt_no: str) -> str:
        """Backward-compatibility for frame dissection calls."""
        return self.execute_tshark_command(f"tshark -V", room)

    @staticmethod
    def get_tshark_manual() -> str:
        return """
┌── TSHARK OT QUICK REFERENCE & MANUAL (UCL INDUSTRIEL NETVÆRK) ────────────────
│ tshark er kommandolinje-udgaven af Wireshark til netværkssniffing og analyse.
│
│ GRUNDLÆGGENDE SYNTAKS:
│   tshark [flag] -Y "<display-filter>"
│
│ VIGTIGE DISPLAY-FILTRE FOR INDUSTRIELLE PROTOKOLLER (OT / ICS):
│   • Modbus TCP (Port 502 - Pumpehuset):
│       tshark -Y "modbus"                   (Viser al Modbus TCP trafik)
│       tshark -Y "modbus.func_code == 3"    (Kun FC 03: Read Holding Registers / SCADA telemetri)
│       tshark -Y "modbus.func_code == 6"    (Kun FC 06: Write Single Register / Sabotagekald)
│       tshark -Y "modbus.func_code == 16"   (Kun FC 16: Write Multiple Registers)
│
│   • PROFINET / DCP (Layer 2 - Ventil-øen):
│       tshark -Y "pn_dcp"                   (PROFINET Discovery & Configuration Protocol)
│       tshark -Y "b8:27:eb"                 (Filtrer på Raspberry Pi OUI MAC-præfiks)
│       tshark -Y "pn_rt"                    (PROFINET Real-Time cyklisk I/O)
│
│   • Siemens S7comm (Port 102 - El-tavlen):
│       tshark -Y "s7comm"                   (Siemens S7-1500 kommunikation)
│       tshark -Y "s7comm.param.func == 0x05"(Uautoriserede PUT/GET job-kald)
│
│   • OPC UA (Port 4840 - Kontrolrummet):
│       tshark -Y "opcua"                    (OPC UA Binary Protocol)
│
│ NYTTIGE FLAG:
│   -V             Fuld protokol-dissekering (viser alle OSI-lag og felter)
│   -c <tal>       Stop opsamling efter <tal> pakker (f.eks. 'tshark -c 5')
│   -T fields -e   Udtræk specifikke felter (f.eks. 'tshark -T fields -e ip.src')
│   -i <interface> Lyt på specifik grænseflade (f.eks. 'tshark -i eth0')
└───────────────────────────────────────────────────────────────────────────────
""".strip()


# Backward-compatible alias
WiresharkSniffer = TSharkEngine


class AutocompleteHelper:
    """Provides shell auto-completion for OT commands and components."""

    COMMANDS = [
        "tshark", "tshark -Y \"modbus\"", "tshark -Y \"modbus.func_code == 6\"",
        "tshark -Y \"modbus.func_code == 3\"", "tshark -Y \"pn_dcp\"",
        "tshark -Y \"s7comm\"", "tshark -Y \"opcua\"", "tshark -V", "man tshark", "cheat tshark",
        "firewall rule add --allow-fc 3 --drop-fc 6", "firewall rule add --drop-fc 6",
        "firewall status", "firewall workbench", "switch workbench",
        "undersøg", "gå til", "tal med", "tag offline backup", "konfigurer tia portal",
        "sikr pi i faraday-pose", "smid pi i skraldespand", "gem pi til genbrug",
        "godkend scada certifikat", "aktiver opc kryptering", "deaktiver anonymous opc",
        "frakobl 4g-router", "indberet hændelse", "vis evidens", "eksporter rapport",
        "hjælp", "status", "rygsæk", "rundtur", "techsupport", "revisor", "tilstand",
    ]

    TARGETS = [
        "pumpehuset", "ventil-øen", "el-tavlen", "kontrolrummet", "indgangen",
        "pumpe 2", "frekvensomformer", "ts35 din-skinne", "scada", "ventiler", "switch",
        "kabelbakke", "rogue raspberry pi", "s7-1500", "sikkerhedsrelæ k1",
        "opc ua server", "4g-router", "hans", "kirsten",
    ]

    @classmethod
    def get_matches(cls, prefix: str) -> list[str]:
        p = prefix.strip().lower()
        if not p:
            return []

        for verb in ("gå til ", "gaa til ", "undersøg ", "undersoeg ", "tal med "):
            if p.startswith(verb):
                sub = p[len(verb):]
                return [f"{verb}{t}" for t in cls.TARGETS if t.startswith(sub)]

        matches = [cmd for cmd in cls.COMMANDS if cmd.startswith(p)]
        return matches
