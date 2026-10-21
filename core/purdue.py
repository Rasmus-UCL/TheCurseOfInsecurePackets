"""Purdue Enterprise Reference Architecture (PERA) & IEC 62443 Models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PurdueLevel:
    level: float
    name: str
    description: str
    iec_sl_target: str
    typical_devices: tuple[str, ...]


PURDUE_LEVELS = {
    0.0: PurdueLevel(
        0.0,
        "Level 0: Physical Process",
        "Pumper, ventiler, sensorer, rørledninger og fysiske aktuatorer.",
        "SL-1 / Fysisk sikring",
        ("Centrifugalpumper", "Manometre", "Magnetventiler", "Flowmålere"),
    ),
    1.0: PurdueLevel(
        1.0,
        "Level 1: Basic Process Control & Drev",
        "Frekvensomformere, ventil-øer, decentrale I/O (ET 200SP) og sikkerheds-PLC.",
        "IEC 62443-3-3 SL-2",
        ("SINAMICS VFD", "Festo Ventil-ø", "Siemens ET 200SP", "Modbus TCP"),
    ),
    2.0: PurdueLevel(
        2.0,
        "Level 2: Supervisory Control",
        "Lokale touchpaneler (HMI), proces-PLC'er og automationsceller.",
        "IEC 62443-3-3 SL-2",
        ("Siemens S7-1500 (CPU 1516F)", "Comfort HMI Panel", "PROFINET RT"),
    ),
    3.0: PurdueLevel(
        3.0,
        "Level 3: Operations & MES",
        "Central SCADA-server, proceshistorik, alarmserver og ingeniørstation.",
        "IEC 62443-3-3 SL-3",
        ("WinCC SCADA Server", "Historian", "TIA Portal Engineering Station"),
    ),
    3.5: PurdueLevel(
        3.5,
        "Level 3.5: Industrial DMZ (IDMZ)",
        "Adskiller OT (Level 0-3) fra IT (Level 4). Ingen direkte trafik må krydse IDMZ.",
        "IEC 62443-3-2 Conduits & Dual Firewalls",
        ("OPC UA Reverse Proxy", "Jump Host / Bastion", "Data Diode / Replica"),
    ),
    4.0: PurdueLevel(
        4.0,
        "Level 4: Enterprise Network",
        "Kontor-IT, ERP, administration, e-mail og adgangskontrol.",
        "ISO 27001 / NIS2 Art. 21",
        ("Kontor-PC'er", "ERP Server", "Hovedindgang Adgangskontrol"),
    ),
}
