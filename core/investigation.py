"""Forensic Investigation & Clue Board Engine for The Curse of Insecure Packets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from models import Clue, MetricValues, Suspect

if TYPE_CHECKING:
    pass


class InvestigationManager:
    """Manages forensic clues, suspects, hypotheses and the case board (sagstavle)."""

    def __init__(self) -> None:
        self.true_culprit_id: str = "lars_ex_tekniker"
        self.clues: dict[str, Clue] = self._init_clues()
        self.suspects: dict[str, Suspect] = self._init_suspects()
        self.prime_suspect_id: str | None = None

    def configure_dynamic_case(self, culprit_id: str, room_variants: dict[str, str]) -> None:
        """Dynamically adapt clue texts, forensic analyses, and suspect links to the active variants and true culprit."""
        if culprit_id not in self.suspects:
            culprit_id = "lars_ex_tekniker"
        self.true_culprit_id = culprit_id

        # Reset base suspicion scores so evidence drives the deduction
        base_scores = {
            "lars_ex_tekniker": 25,
            "morten_pumper": 25,
            "kim_operatoer": 25,
            "apt_shadowh2o": 25,
            "systemisk_fejl": 15,
        }
        base_scores[culprit_id] = 30
        for sid, score in base_scores.items():
            if sid in self.suspects:
                self.suspects[sid].suspicion_score = score

        # 1. Pumpehuset variant clues
        p_var = room_variants.get("pumpehuset", "A")
        if p_var == "B":
            self.clues["spor_modbus_flood"].title = "Uautoriseret SNMPv1 SetRequest ('private') & ARP-Spoofing fra 192.168.1.99"
            self.clues["spor_modbus_flood"].description = (
                "VFD'ens interne frekvens-OID overskrives til 120 Hz via SNMPv1 community 'private' (UDP 161) under aktiv ARP-poisoning."
            )
            self.clues["spor_modbus_flood"].analysis = (
                "Angriberen misbruger en åben SNMPv1-agent med standard-community 'private' og omdirigerer PLC-trafikken med falske ARP-svar."
            )
        elif p_var == "C":
            self.clues["spor_modbus_flood"].title = "Ukrypteret HTTP Web-API Override (admin/admin) på VFD Port 80"
            self.clues["spor_modbus_flood"].description = (
                "HTTP POST /api/vfd/override tvinger SINAMICS G120 i 120 Hz manuel tvangsdrift via standard-login (admin:admin)."
            )
            self.clues["spor_modbus_flood"].analysis = (
                "VFD'ens indbyggede diagnoseserver stod åben på TCP port 80 med fabriks-adgangskode, så feltbus-setpunktet blev kapret."
            )

        # 2. Ventil-øen variant clues
        v_var = room_variants.get("ventil-oen", "A")
        if v_var == "B":
            self.clues["spor_dcp_storm"].title = "IEEE 802.1Q VLAN Priority-Stripping & Falske LLDP-Nabopakker"
            self.clues["spor_dcp_storm"].description = (
                "Kritisk RT-trafik får fjernet sine 802.1Q Priority 6 tags, mens falske LLDP-pakker forvirrer topologien."
            )
            self.clues["spor_dcp_storm"].analysis = (
                "En aktiv netværks-tap manipulerer Layer-2 headers direkte i ventil-klemkassen for at fremprovokere pakketab og ventil-svingninger."
            )
            self.clues["spor_sort_boks"].title = "Skjult Aktiv LAN-Tap & Packet-Injector i Ventil-Klemkassen"
            self.clues["spor_sort_boks"].description = (
                "En lille sort mikro-tap koblet ind mellem ventil-øens klemrække og den uadministrerede D-Link switch."
            )
        elif v_var == "C":
            self.clues["spor_dcp_storm"].title = "Ukrypteret MQTT Kommandostorm (Port 1883) mod Smart-Ventiler"
            self.clues["spor_dcp_storm"].description = (
                "En strøm af uautentificerede MQTT PUBLISH 'nordic/valves/all/set=oscillate' tvinger ventilerne til at klapre."
            )
            self.clues["spor_dcp_storm"].analysis = (
                "IIoT-sidekanalen på ventil-øen kørte ukrypteret MQTT uden TLS eller broker-autentificering."
            )
            self.clues["spor_sort_boks"].title = "Uautoriseret ESP32/MQTT-Bro skjult under kabelbakken"
            self.clues["spor_sort_boks"].description = (
                "Et hjemmebygget ESP32-modul med Ethernet-shield sat direkte i den åbne D-Link switch under kabelbakken."
            )

        # 3. El-tavlen variant clues
        e_var = room_variants.get("el-tavlen", "A")
        if e_var == "B":
            self.clues["spor_plc_stop_buffer"].title = "S7-1516F Diagnostic Buffer: 'F-Safety Watchdog Timeout i OB35 (0x75E1)'"
            self.clues["spor_plc_stop_buffer"].description = (
                "Fail-Safe OB35 cyklustiden er blevet manipuleret til 500 ms (grænse: 100 ms), hvilket udløste et F-CPU Safety-STOP."
            )
            self.clues["spor_plc_stop_buffer"].analysis = (
                "F-Safety adgangskoden var deaktiveret, hvilket tillod fjernændring af sikkerheds-watchdoggen uden hardware-nøgle."
            )
        elif e_var == "C":
            self.clues["spor_plc_stop_buffer"].title = "S7-1500 Diagnostic Buffer: 'NTP Time-Jump til 1970 & TLS Certifikat-Fejl'"
            self.clues["spor_plc_stop_buffer"].description = (
                "Uautentificerede NTP-pakker (UDP 123) har nulstillet PLC-uret til 1970, så X.509/TLS-sikkerhedsforbindelsen gik i STOP."
            )
            self.clues["spor_plc_stop_buffer"].analysis = (
                "PLC'en accepterede usigneret NTP-tidssynkronisering fra enhver vært på det flade OT-netværk."
            )

        # 4. Kontrolrummet variant clues
        k_var = room_variants.get("kontrolrummet", "A")
        if k_var == "B":
            self.clues["spor_4g_dongle"].title = "Skjult Wi-Fi Access Point under gulvet ved Patchpanelet"
            self.clues["spor_4g_dongle"].description = (
                "Et kompakt dual-band Wi-Fi AP gemt under det hævede gulv i kontrolrummet, koblet direkte i SCADA-switchen."
            )
            self.clues["spor_4g_dongle"].analysis = (
                "Giver trådløs adgang fra parkeringspladsen uden om perimeter-firewallen direke ind i Level 2/3."
            )
            self.clues["spor_opc_leak"].title = "Kompromitteret Leverandør-Certifikat & Åben OPC UA SecurityPolicy"
            self.clues["spor_opc_leak"].description = (
                "Et stjålet/udløbet X.509 leverandørcertifikat samt tilladt 'SecurityMode: None' giver fuld læse-/skriveadgang i SCADA."
            )
        elif k_var == "C":
            self.clues["spor_4g_dongle"].title = "Uautoriseret Mini-VPN/RDP Tunnel-Boks bag IDMZ-Patchpanelet"
            self.clues["spor_4g_dongle"].description = (
                "En lille hardware-tunnelboks der viderestiller TCP port 3389 (Remote Desktop) direkte til SCADA-operatørstationen."
            )
            self.clues["spor_4g_dongle"].analysis = (
                "Omgår IDMZ-segmenteringen og eksponerer SCADA HMI-sessionen uden Multi-Factor Authentication (NIS2 Art. 21.2.j)."
            )

        # 5. Culprit-specific forensic signatures & clue associations
        if culprit_id == "lars_ex_tekniker":
            self.clues["spor_usb_backup"].title = "USB-stik mærket 'LARS - TIA V16 BACKUP'"
            self.clues["spor_usb_backup"].description = (
                "En efterladt USB-nøgle i el-tavlen med Lars' initialer og et projektarkiv uden adgangskode."
            )
            self.clues["spor_usb_backup"].analysis = (
                "Metadata i projektfilen viser, at brugeren 'LKO_ENG' kompilerede angrebs-scriptet med eksakt kendskab til værkets DB-struktur."
            )
            self.clues["spor_usb_backup"].associated_suspects = ["lars_ex_tekniker"]
            self.clues["spor_sort_boks"].associated_suspects = ["lars_ex_tekniker"]
            self.clues["spor_mac_oui"].associated_suspects = ["lars_ex_tekniker"]
            self.clues["spor_modbus_flood"].associated_suspects = ["lars_ex_tekniker", "apt_shadowh2o"]
            self.clues["spor_dcp_storm"].associated_suspects = ["lars_ex_tekniker"]
            self.clues["spor_plc_stop_buffer"].associated_suspects = ["lars_ex_tekniker", "systemisk_fejl"]

        elif culprit_id == "morten_pumper":
            self.clues["spor_morten_rapport"].title = "Hans' vidneudsagn & Service-log: 'Morten fra Hydropump var alene i alle 4 zoner tirsdag'"
            self.clues["spor_morten_rapport"].description = (
                "Adgangsloggen viser, at Morten Vestergaard lånte hovednøglen tirsdag og besøgte både pumpehus, ventil-ø og el-tavle."
            )
            self.clues["spor_morten_rapport"].analysis = (
                "PÅFALDENDE: Dagen efter sendte Hydropump Nordic A/S et tilbud på en 'Akut 24/7 Total-Servicekontrakt' til 1,8 mio. kr.!"
            )
            self.clues["spor_morten_rapport"].associated_suspects = ["morten_pumper"]
            self.clues["spor_usb_backup"].title = "USB-stik mærket 'HYDROPUMP NORDIC - SERVICE DIAG V4'"
            self.clues["spor_usb_backup"].description = (
                "En rød leverandør-USB efterladt i el-tavlen med Mortens kalibreringsværktøj og et skjult stress-test script."
            )
            self.clues["spor_usb_backup"].analysis = (
                "Scriptet 'pump_stress_induce.py' er signeret af brugerkontoen 'mve@hydropump.dk' og programmeret til at udløse nedbrud fredag."
            )
            self.clues["spor_usb_backup"].associated_suspects = ["morten_pumper"]
            self.clues["spor_sort_boks"].description += " På undersiden sidder et inventarmærke fra 'Hydropump Field Test Lab #04'."
            self.clues["spor_sort_boks"].associated_suspects = ["morten_pumper"]
            self.clues["spor_mac_oui"].associated_suspects = ["morten_pumper"]
            self.clues["spor_modbus_flood"].associated_suspects = ["morten_pumper"]
            self.clues["spor_dcp_storm"].associated_suspects = ["morten_pumper"]
            self.clues["spor_plc_stop_buffer"].associated_suspects = ["morten_pumper"]
            self.clues["spor_4g_dongle"].associated_suspects = ["morten_pumper", "kim_operatoer"]

        elif culprit_id == "apt_shadowh2o":
            self.clues["spor_usb_backup"].title = "Kryptografisk Ransomware-Staging Note ('SHADOWH2O_README.TXT') i El-tavlen"
            self.clues["spor_usb_backup"].description = (
                "I PLC'ens hukommelseskort-slot ligger en droppet payload-fil med C2-signaturer fra trusselsgruppen ShadowH2O."
            )
            self.clues["spor_usb_backup"].analysis = (
                "C2-serverens TLS-fingerprint matcher Europol-advarslen mod APT-gruppen ShadowH2O, som angriber nordiske vandværker."
            )
            self.clues["spor_usb_backup"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_mac_oui"].title = "Spoofed MAC & C2-Beacon til Ekstern Tor-Relay (ShadowH2O)"
            self.clues["spor_mac_oui"].description = (
                "Netværksopsamlingen viser krypterede C2-heartbeats hvert 30. sekund gennem den uautoriserede fjernadgang i kontrolrummet."
            )
            self.clues["spor_mac_oui"].analysis = (
                "Angriberen er kommet ind udefra via den usikrede fjernadgang i kontrolrummet og har pivoteret direkte ned til feltniveauet!"
            )
            self.clues["spor_mac_oui"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_sort_boks"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_modbus_flood"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_manometer_rystelser"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_dcp_storm"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_plc_stop_buffer"].associated_suspects = ["apt_shadowh2o"]
            self.clues["spor_opc_leak"].associated_suspects = ["apt_shadowh2o"]

        elif culprit_id == "kim_operatoer":
            self.clues["spor_usb_backup"].title = "USB-stik mærket 'KIM D. - NATTEVAGT AUTO-BYPASS SCRIPTS'"
            self.clues["spor_usb_backup"].description = (
                "En personlig USB-nøgle i el-tavlen med hjemmelavede Python-scripts til at tvinge ventiler og pumper uden om SCADA-alarmerne."
            )
            self.clues["spor_usb_backup"].analysis = (
                "Kim forsøgte at skjule en fejlbetjening fra torsdag nat ved at overstyre PLC'en og VFD'en med uautoriserede bypass-scripts!"
            )
            self.clues["spor_usb_backup"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_kim_nattevagt"].title = "SCADA & Terminal-Log: 'Bruger KIM_D kørte override_all_zones.sh kl. 03:14'"
            self.clues["spor_kim_nattevagt"].description = (
                "Kommandohistorikken viser, at Kim Dahl fra sin nattevagt-session selv satte den sorte boks op og udløste overstyringen."
            )
            self.clues["spor_kim_nattevagt"].analysis = (
                "Entydigt digitalt spor: Kim opsatte ikke kun ulovlig fjernadgang, men kørte også de fatale bypass-kommandoer for at dække over en tørlægning."
            )
            self.clues["spor_kim_nattevagt"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_sort_boks"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_mac_oui"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_modbus_flood"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_dcp_storm"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_plc_stop_buffer"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_4g_dongle"].associated_suspects = ["kim_operatoer"]
            self.clues["spor_opc_leak"].associated_suspects = ["kim_operatoer"]

    def _init_suspects(self) -> dict[str, Suspect]:
        return {
            "morten_pumper": Suspect(
                id="morten_pumper",
                name="Morten Vestergaard (Hydropump Nordic A/S)",
                role="Ekstern Servicepartner & Pumpe-ingeniør",
                theory="Efterlod et aggressivt polling-loop eller test-script under pumpeoptimering tirsdag.",
                opportunity="Havde fysisk og logisk adgang til pumpehuset tirsdag eftermiddag med leverandør-laptop.",
                motive="Uagtsom teknisk fejl, eller overfakturering for akut nedbrudsservice i weekenden.",
                suspicion_score=20,
                status="Aktiv efterforskning",
            ),
            "lars_ex_tekniker": Suspect(
                id="lars_ex_tekniker",
                name="Lars Kofoed",
                role="Tidligere OT-Automationstekniker (fyret for 2 mdr. siden)",
                theory="Placerede en fysisk bagdør (Rogue Pi) og udnytter standardadgangskoder til hævnaktion.",
                opportunity="Kender alle IP-adresser, PLC-databaser (DB1), kabelføringer og svagheder i anlægget.",
                motive="Bitterhed over uretmæssig afskedigelse og ubetalt overarbejde.",
                suspicion_score=35,
                status="Aktiv efterforskning",
            ),
            "kim_operatoer": Suspect(
                id="kim_operatoer",
                name="Kim Dahl",
                role="Intern Procesoperatør (Natholdet)",
                theory="Opsatte en uautoriseret 4G-router for at kunne overvåge og kvittere SCADA-alarmer hjemmefra.",
                opportunity="Alene på nattevagt i kontrolrummet med fri adgang til bagsiden af server-racket.",
                motive="Bekvemmelighed og dovenskab; ville undgå at køre ind på værket om natten.",
                suspicion_score=25,
                status="Aktiv efterforskning",
            ),
            "apt_shadowh2o": Suspect(
                id="apt_shadowh2o",
                name="ShadowH2O / DarkVolt Syndikatet",
                role="Ekstern Cyberkriminel Trusselsaktør (APT)",
                theory="Målrettet OT-angreb mod kritisk drikkevandsinfrastruktur med henblik på afpresning (ransomware).",
                opportunity="Udnytter internet-eksponerede protokoller (OPC UA, 4G uplink) og ubeskyttet Layer 2.",
                motive="Geopolitisk disruption eller økonomisk afpresning under trussel om forgiftning/tørlægning.",
                suspicion_score=30,
                status="Aktiv efterforskning",
            ),
            "systemisk_fejl": Suspect(
                id="systemisk_fejl",
                name="Systemisk Konfigurationskollaps & Teknisk Gæld",
                role="Intern Drifts- & Netværksanomali",
                theory="Ingen fjendtlig aktør – anlægget knækker under akkumuleret teknisk gæld og broadcast-storme.",
                opportunity="Fladt netværk uden VLAN, forældede firmwareversioner og defekt I/O-udstyr.",
                motive="Ingen – ren teknisk entropi og mangelfuld vedligeholdelse.",
                suspicion_score=15,
                status="Aktiv efterforskning",
            ),
        }

    def _init_clues(self) -> dict[str, Clue]:
        return {
            "spor_modbus_flood": Clue(
                id="spor_modbus_flood",
                title="Højhastigheds Modbus FC06 skrivninger fra 192.168.1.99",
                category="Netværk",
                discovery_room="pumpehuset",
                description="Uautoriseret vært oversvømmer VFD med Modbus Function Code 06 til register 40001 (120 Hz).",
                analysis="Pakkerne kommer fra 192.168.1.99, som ikke optræder i værkets IP-plan. Frekvensen overskrider motorens nominelle grænse med 140%!",
                associated_suspects=["lars_ex_tekniker", "apt_shadowh2o", "morten_pumper"],
            ),
            "spor_manometer_rystelser": Clue(
                id="spor_manometer_rystelser",
                title="Fysiske trykstød på 14.8 Bar & Manometerrystelser",
                category="Fysisk",
                discovery_room="pumpehuset",
                description="Manometeret ryster faretruende på Pumpe 2, mens SCADA viser 'ALT NORMALT 3.2 BAR'.",
                analysis="Klassisk falsk telemetri (Stuxnet-stil). Operatøren vildledes, mens det fysiske rørnet overbelastes hydraulisk.",
                associated_suspects=["apt_shadowh2o", "lars_ex_tekniker"],
            ),
            "spor_morten_rapport": Clue(
                id="spor_morten_rapport",
                title="Hans' vidneudsagn: 'Morten fra Hydropump var her tirsdag'",
                category="Vidneudsagn",
                discovery_room="pumpehuset",
                description="Hans husker, at Morten justerede frekvensomformeren i tirsdags og skyndte sig af sted.",
                analysis="Tidsmæssigt sammenfald med de første trykudsving. Var det en bevidst handling eller en glemt testprofil?",
                associated_suspects=["morten_pumper"],
            ),
            "spor_dcp_storm": Clue(
                id="spor_dcp_storm",
                title="PROFINET DCP Set Name broadcast-storm",
                category="Netværk",
                discovery_room="ventil-oen",
                description="Lag-2 Ethernet broadcast-storm med PROFINET DCP pakker manipulerer ventil-stationernes navne.",
                analysis="PROFINET DCP har ingen kryptering eller adgangskontrol. Kræver direkte fysisk tilslutning til det lokale Layer 2 domæne.",
                associated_suspects=["lars_ex_tekniker", "apt_shadowh2o"],
            ),
            "spor_sort_boks": Clue(
                id="spor_sort_boks",
                title="Optapet sort boks skjult i kabelbakke (Rogue Pi)",
                category="Fysisk",
                discovery_room="ventil-oen",
                description="En uautoriseret sort boks med Raspberry Pi 4 tilsluttet en unmanaged D-Link switchport.",
                analysis="Hardware-implantat strømforsynet via PoE. Kører automatiseret angrebssuite med Scapy og Modbus-scripts.",
                associated_suspects=["lars_ex_tekniker", "apt_shadowh2o", "kim_operatoer"],
            ),
            "spor_mac_oui": Clue(
                id="spor_mac_oui",
                title="MAC-adresse OUI B8:27:EB fundet i netværkstrafik",
                category="Netværk",
                discovery_room="ventil-oen",
                description="Netværksopsamling afslører MAC B8:27:EB:AA:12:34, som tilhører Raspberry Pi Foundation.",
                analysis="Bekræfter fysisk fremmedlegeme i produktionscellen. Bevis for brud på fysisk adgangskontrol.",
                associated_suspects=["lars_ex_tekniker", "apt_shadowh2o"],
            ),
            "spor_plc_stop_buffer": Clue(
                id="spor_plc_stop_buffer",
                title="S7-1500 Diagnostic Buffer: 'DB1 Write Failure & Stop Event'",
                category="Systemlog",
                discovery_room="el-tavlen",
                description="PLC'ens interne logbog viser gentagne fejlkoder (0x8104) og korrumperede værdier i DataBlock 1.",
                analysis="Angriberen anvendte rå S7comm (port 102) til at overskrive DB1, fordi 'Tillad PUT/GET' stod ubeskyttet åben.",
                associated_suspects=["lars_ex_tekniker", "apt_shadowh2o", "systemisk_fejl"],
            ),
            "spor_usb_backup": Clue(
                id="spor_usb_backup",
                title="USB-stik mærket 'LARS - TIA V16 BACKUP'",
                category="Konfiguration",
                discovery_room="el-tavlen",
                description="En efterladt USB-nøgle med et projektarkiv, hvor beskyttelsesniveauet er sat til 'Ingen adgangskode'.",
                analysis="Dokumenterer at Lars efterlod centrale ingeniørprojekter i en sårbar tilstand uden password-hærdning.",
                associated_suspects=["lars_ex_tekniker"],
            ),
            "spor_4g_dongle": Clue(
                id="spor_4g_dongle",
                title="Teltonika RUT240 4G-router gemt bag SCADA-rack",
                category="Fysisk",
                discovery_room="kontrolrummet",
                description="En aktiv cellulær router sat i vægkontakten bag racket med LAN-kabel direkte til SCADA-switchen.",
                analysis="Klassisk Shadow-IT. Skaber en direkte tunnel udenom perimeter-firewallen og eksponerer anlægget mod internettet.",
                associated_suspects=["kim_operatoer", "morten_pumper"],
            ),
            "spor_opc_leak": Clue(
                id="spor_opc_leak",
                title="OPC UA Server med SecurityPolicy: None & Anonymous",
                category="Konfiguration",
                discovery_room="kontrolrummet",
                description="OPC UA endpoint opc.tcp://0.0.0.0:4840 tillader uautentificeret læsning af hele adresse-rummet.",
                analysis="Enhver med netværksadgang kan aflæse samtlige flow-, tryk- og kemikalieværdier uden certifikat.",
                associated_suspects=["kim_operatoer", "systemisk_fejl", "apt_shadowh2o"],
            ),
            "spor_kim_nattevagt": Clue(
                id="spor_kim_nattevagt",
                title="SCADA Session Log: Natlige logins fra IP 10.144.20.1",
                category="Vidneudsagn",
                discovery_room="kontrolrummet",
                description="Auditloggen viser administrative login-sessioner kl. 03:14 fra en mobil IP-adresse.",
                analysis="Matcher Kims nattevagt. Viser at den uautoriserede 4G-router rent faktisk er blevet anvendt til fjernadgang.",
                associated_suspects=["kim_operatoer"],
            ),
        }

    # -------------------------------------------------------------------------
    # INVESTIGATION ACTIONS
    # -------------------------------------------------------------------------
    def reset_for_main_campaign(self) -> None:
        """Clear any tutorial clues, analyses, notes, and prime suspect so the real campaign starts with a clean Case Board."""
        self.prime_suspect_id = None
        for c in self.clues.values():
            c.discovered = False
            c.analyzed = False
            c.discovered_time = ""
        base_scores = {
            "lars_ex_tekniker": 25,
            "morten_pumper": 25,
            "kim_operatoer": 25,
            "apt_shadowh2o": 25,
            "systemisk_fejl": 15,
        }
        if self.true_culprit_id in base_scores:
            base_scores[self.true_culprit_id] = 30
        for sid, s in self.suspects.items():
            s.status = "Aktiv efterforskning"
            s.notes = []
            s.suspicion_score = base_scores.get(sid, 20)

    def discover_clue(self, clue_id: str, simulated_time: str = "") -> tuple[bool, Clue | None]:
        """Mark a clue as discovered and update suspect suspicion scores."""
        clue = self.clues.get(clue_id)
        if not clue:
            return False, None
        if clue.discovered:
            return False, clue

        clue.discovered = True
        clue.discovered_time = simulated_time or "Dag 1, time 1"

        # Update suspicion scores for linked suspects
        for susp_id in clue.associated_suspects:
            if susp_id in self.suspects:
                susp = self.suspects[susp_id]
                susp.suspicion_score = min(100, susp.suspicion_score + 15)
                if clue.title not in susp.notes:
                    susp.notes.append(clue.title)

        return True, clue

    def get_discovered_clues(self) -> list[Clue]:
        return [c for c in self.clues.values() if c.discovered]

    def get_unanalyzed_clues(self) -> list[Clue]:
        return [c for c in self.clues.values() if c.discovered and not c.analyzed]

    def get_analyzed_clues(self) -> list[Clue]:
        return [c for c in self.clues.values() if c.discovered and c.analyzed]

    def get_analyzed_clues_for_suspect(self, suspect_id: str) -> list[Clue]:
        return [
            c for c in self.clues.values()
            if c.discovered and c.analyzed and suspect_id in c.associated_suspects
        ]

    def get_clue(self, clue_id: str) -> Clue | None:
        return self.clues.get(clue_id)

    def get_suspect(self, suspect_id: str) -> Suspect | None:
        return self.suspects.get(suspect_id)

    def set_prime_suspect(self, suspect_id: str) -> tuple[bool, str]:
        if suspect_id not in self.suspects:
            return False, f"Ukendt mistænkt ID '{suspect_id}'. Brug 'mistænkte' for at se listen."

        for s in self.suspects.values():
            if s.status == "Hovedmistænkt":
                s.status = "Aktiv efterforskning"

        susp = self.suspects[suspect_id]
        susp.status = "Hovedmistænkt"
        self.prime_suspect_id = suspect_id
        return True, f"🎯 [SAGSTAVLE OPDATERET]: {susp.name} er nu udpeget som din primære arbejdshypotese!"

    # -------------------------------------------------------------------------
    # FORMATTING & CASE BOARD
    # -------------------------------------------------------------------------
    def _render_bar(self, value: int, width: int = 10) -> str:
        filled = int((value / 100) * width)
        return "█" * filled + "░" * (width - filled)

    def format_clue_board(self, metrics: MetricValues, game_mode: str = "teach") -> str:
        """Render full ASCII/Unicode Case Board (Sagstavle)."""
        discovered = self.get_discovered_clues()
        unanalyzed = self.get_unanalyzed_clues()
        is_exam = (game_mode == "exam")
        lines: list[str] = [
            "================================================================================",
            "                 🕵️  SAGSTAVLE – NORDIC H2O CYBER-EFTERFORSKNING               ",
            "================================================================================",
            " SÅDAN BRUGER DU SAGSTAVLEN (3 TRIN):",
            "   1. Find spor ved at undersøge udstyr, køre 'tshark' og tale med Hans.",
            "   2. Klik på '⚠️ NYT SPOR' til højre (eller 'analyser spor <id>') for at koble det til mistænkte.",
            "   3. Klik på en mistænkt til venstre (eller 'anklag <id>') for at vælge din ⭐ Hovedmistænkt.",
            "--------------------------------------------------------------------------------",
            " METRIKKER FOR ANLÆG OG INDSATS:",
            f"   🔧 Drift:      [{self._render_bar(metrics.drift)}] {metrics.drift:3d}%  (Uptime & vandforsyning)",
            f"   🛡️  Sikkerhed:  [{self._render_bar(metrics.sikkerhed)}] {metrics.sikkerhed:3d}%  (Segmentering & zoner)",
            f"   📜 Compliance: [{self._render_bar(metrics.compliance)}] {metrics.compliance:3d}%  (NIS2 & dokumentation)",
            f"   🤝 Tillid:     [{self._render_bar(metrics.tillid)}] {metrics.tillid:3d}%  (Hans' partnerskab & moral)",
            "--------------------------------------------------------------------------------",
            " MISTÆNKTE & ARBEJDSHYPOTESER (Klik på kortet eller skriv 'anklag <id>'):",
        ]

        suspect_list = (
            list(self.suspects.values())
            if is_exam
            else sorted(self.suspects.values(), key=lambda x: x.suspicion_score, reverse=True)
        )
        for s in suspect_list:
            status_marker = "⭐ [HOVEDMISTÆNKT]" if s.status == "Hovedmistænkt" else f"[{s.status}]"
            if is_exam:
                lines.append(f"   • {s.name:<38}  {status_marker}")
                lines.append(f"     ID: {s.id:<18} Rolle: {s.role}")
            else:
                linked_count = len(self.get_analyzed_clues_for_suspect(s.id))
                lines.append(
                    f"   • {s.name:<38} [{self._render_bar(s.suspicion_score, 8)}] {s.suspicion_score:2d}%  {status_marker}"
                )
                lines.append(f"     ID: {s.id:<18} Rolle: {s.role} | 🔗 Analyserede beviser: {linked_count}")

        lines.extend([
            "--------------------------------------------------------------------------------",
            f" OPDAGEDE SPOR ({len(discovered)} af {len(self.clues)} fundet | {len(unanalyzed)} mangler analyse):",
        ])

        if not discovered:
            lines.append("   (Ingen spor fundet endnu. Undersøg anlægget med tshark, hotspots og logbøger!)")
        else:
            categories = ["Netværk", "Fysisk", "Systemlog", "Vidneudsagn", "Konfiguration"]
            for cat in categories:
                cat_clues = [c for c in discovered if c.category == cat]
                if cat_clues:
                    lines.append(f"   [{cat.upper()}]:")
                    for c in cat_clues:
                        state_tag = "✅ [ANALYSERET]" if c.analyzed else "⚠️ [NYT - KLIK FOR ANALYSE!]"
                        lines.append(f"     🔍 [{c.id}] {state_tag}: {c.title} ({c.discovery_room})")

        lines.extend([
            "================================================================================",
            " Værktøjer: 'spor' (detaljeret liste), 'mistænkte' (profiler), 'analyser spor <id>'",
            "================================================================================",
        ])
        return "\n".join(lines)

    def format_clues_list(self, game_mode: str = "teach") -> str:
        discovered = self.get_discovered_clues()
        if not discovered:
            return "Ingen spor fundet endnu. Undersøg pumper, kabler, logs eller kør tshark for at finde spor."

        is_exam = (game_mode == "exam")
        lines = ["\n🔍 [OPDAGEDE SPOR I EFTERFORSKNINGEN]:"]
        for c in discovered:
            status_str = "✅ ANALYSERET" if c.analyzed else "⚠️ NYT (Ikke analyseret endnu)"
            lines.append(f"\n--- Spor ID: {c.id} [{c.category.upper()}] — {status_str} ---")
            lines.append(f"Titel:      {c.title}")
            lines.append(f"Lokalitet:  {c.discovery_room} (Fundet: {c.discovered_time})")
            lines.append(f"Beskrivelse:{c.description}")
            if c.analyzed:
                if is_exam:
                    lines.append(f"Analyse:    {c.analysis}")
                else:
                    lines.append(f"Peger mod:  {', '.join(c.associated_suspects)}")
            else:
                lines.append("Peger mod:  [Ukendt indtil sporet analyseres med 'analyser spor " + c.id + "']")
        lines.append("\nTip: Skriv 'analyser spor <id>' (eller klik på sporet på Sagstavlen) for dybdegående teknisk analyse.")
        return "\n".join(lines)

    def format_clue_analysis(self, clue_id: str, game_mode: str = "teach") -> str:
        clue = self.clues.get(clue_id)
        if not clue:
            return f"Ukendt spor '{clue_id}'. Skriv 'spor' for at se fundne spor."
        if not clue.discovered:
            return f"Sporet '{clue_id}' er endnu ikke opdaget på anlægget."

        first_time = not clue.analyzed
        clue.analyzed = True
        if first_time:
            for susp_id in clue.associated_suspects:
                if susp_id in self.suspects:
                    susp = self.suspects[susp_id]
                    susp.suspicion_score = min(100, susp.suspicion_score + 5)
                    if clue.title not in susp.notes:
                        susp.notes.append(clue.title)

        lines = [
            f"\n🔬 [DYBDE-ANALYSE AF SPOR: {clue.id}] — ✅ BEVIS KOBLET PÅ SAGSTAVLEN",
            f"Titel:      {clue.title}",
            f"Kategori:   {clue.category} | Zone: {clue.discovery_room}",
            f"Fund:       {clue.description}",
            f"\n🧠 OT-TEKNISK VURDERING:",
            f"{clue.analysis}",
        ]
        if game_mode == "exam":
            lines.extend([
                "\n📝 [EKSAMENS-MODE VURDERING]:",
                "Sammenhold selv denne tekniske vurdering med de mistænktes adgang, kompetencer og motiver.",
                "💡 Tip: Klik på en mistænkt til venstre på Sagstavlen (eller skriv 'anklag <id>') for at vælge din ⭐ Hovedmistænkt!",
            ])
        else:
            suspect_names = [
                f"{self.suspects[sid].name} ({sid})" if sid in self.suspects else sid
                for sid in clue.associated_suspects
            ]
            lines.extend([
                f"\n🔗 HYPOTESE-KNYTNING (PEGER MOD MISTÆNKTE):",
                f"Dette spor understøtter teorier vedrørende: {', '.join(suspect_names)}",
                "💡 Tip: Klik på en mistænkt til venstre på Sagstavlen (eller skriv 'anklag <id>') for at vælge din ⭐ Hovedmistænkt!",
            ])
        return "\n".join(lines)

    def format_suspects_list(self, game_mode: str = "teach") -> str:
        is_exam = (game_mode == "exam")
        lines = ["\n👥 [MISTÆNKTE & HYPOTESER FOR HÆNDELSEN]:"]
        for s in self.suspects.values():
            star = "⭐ " if s.status == "Hovedmistænkt" else "   "
            lines.append(f"\n{star}ID: {s.id} ({s.name})")
            lines.append(f"   Rolle:          {s.role}")
            if not is_exam:
                lines.append(f"   Mistankegrad:   [{self._render_bar(s.suspicion_score, 10)}] {s.suspicion_score}%")
            lines.append(f"   Teori:          {s.theory}")
            lines.append(f"   Mulighed/Adgang:{s.opportunity}")
            lines.append(f"   Motiv:          {s.motive}")
            if not is_exam and s.notes:
                lines.append(f"   Knyttede spor:  {', '.join(s.notes)}")
        lines.append("\nTip: Skriv 'anklag <id>' for at fastsætte din hovedmistænkte på sagstavlen.")
        return "\n".join(lines)
