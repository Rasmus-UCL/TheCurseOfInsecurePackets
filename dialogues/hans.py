"""Hans McDonald (Senior Driftstekniker) - Dynamic Dialogue Engine with Situational Memory."""

from __future__ import annotations

import random
from typing import Any


class HansDialogue:
    """Manages Hans McDonald's situational responses, OT anecdotes, and technical advice."""

    def __init__(self) -> None:
        self.talk_count = 0
        self.heard_topics: set[str] = set()

    def get_greeting(self, engine: Any) -> str:
        self.talk_count += 1
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        r = getattr(engine, "room", "indgangen")

        # Situational reactions based on live plant states
        if getattr(engine, "breaker_tripped", False):
            return (
                "Hans taber næsten kaffekoppen: 'Hørte du det brag?! K1-sikringen i Hoved-el-tavlen slog fra! "
                "Det var et klassisk hydraulisk vandslag! Nogen må have hevet stikket til frekvensomformeren midt under fuld last. "
                "Skynd dig over til El-tavlen og nulstil relæet, før motorviklingerne tager skade!'"
            )

        if getattr(engine, "scada_blind", False):
            return (
                "Hans ser nervøst på sin tablet: 'Hov hov! Kontrolrummet melder over radioen, at SCADA er helt sort for Pumpe 2! "
                "Har du blokeret port 502 totalt? Husk nu: Vi kan ikke bare lukke porten blindt som i almindelig IT – "
                "SCADA skal have lov til at læse måleværdierne via Function Code 03, ellers styrer vi i blinde!'"
            )

        if getattr(engine, "plc_defect_stop", False):
            return (
                "Hans ryster på hovedet med alvorlig mine: 'Det ser skidt ud i Hoved-el-tavlen! S7-1500 PLC'en er gået i DEFECTIVE STOP! "
                "Fejlkode 0x4542 betyder CRC-korruption i sikkerhedsblokkene. Rør aldrig ved en PLC under kørsel uden at have "
                "et gyldent offline backup-stik i hånden! Har du dit USB-stik klar?'"
            )

        if getattr(engine, "scada_log_interrupted", False):
            return (
                "Hans sukker tungt: 'Miljøstyrelsens nødtelefon kimer! Da du lukkede port 4840, røg vores lovpligtige miljøovervågning. "
                "I henhold til NIS2 skal vi logge kontinuerligt. Du skal hærdne OPC UA med certifikater frem for at kappe kablet!'"
            )

        if getattr(engine, "cavitation_deadline_active", False):
            return (
                "Hans råber gennem larmen: 'Hører du det skærende hyl?! Det er kavitation! Når modtrykket forsvinder, "
                "imploderer mikroskopiske dampbobler mod skovlhjulene som små kanonslag! "
                "Få den SCALANCE switch op på DIN-skinnen og slut MRP-ringen før pumperne er skrot!'"
            )

        if getattr(engine, "pump_deadline_active", False):
            return (
                "Hans peger med kaffekoppen mod Pumpehuset: 'Hører du sirenen? Manometeret står og hopper på over 130 Bar! "
                "Et centrifugalrør holder ikke til 150 Bar. Brug Wireshark til at se hvem der spammer register 0x0000!'"
            )

        if ch == 1:
            return (
                "Hans McDonald tager en tår af sin kaffe: 'Nå, velkommen til Nordic H2O Utility! "
                "Husk den gyldne regel i procesanlæg: Drift og personsikkerhed kommer altid i første række. "
                "Pumpe 2 opfører sig mærkeligt – gå over i Pumpehuset og kobl din laptop på nettet!'"
            )

        if ch == 2:
            if "pi-removed" not in flags:
                return (
                    "Hans hvisker hemmelighedsfuldt: 'De ventiler danser rundt som til en folkefest. "
                    "Vores lærling mente han så et blåt netværkskabel, der forsvandt op under kabelbakken bag ventilstativerne. "
                    "Det kabel findes ikke i vores P&ID-tegninger! Undersøg den kabelbakke grundigt!'"
                )
            return (
                "Hans nikker anerkendende: 'Godt du fik pillet den rogue Raspberry Pi fra! Nu skal vi bare have "
                "erstattet den gamle D-Link switch med en industriel SCALANCE med MRP-ringstyring.'"
            )

        if ch == 3:
            return (
                "Hans klør sig i skægget: 'S7-1500 PLC'en er hjertet i hele vandforsyningen. "
                "En god automationsteknolog starter altid med en frisk backup på USB. "
                "Dernæst logger du ind via TIA Portal og lukker for ubeskyttet PUT/GET kommunikation!'"
            )

        if ch == 4:
            return (
                "Hans kigger ud over kontrolrummet: 'Kontrolrummet er vores IDMZ. "
                "Der må ALDRIG være direkte adgang fra internettet ind til feltbus-zonerne. "
                "Kig bag SCADA-racket – der hænger en 4G-router som en ekstern montør 'glemte' under nedlukningen sidste måned!'"
            )

        if ch == 5:
            return (
                "Hans retter på sit kedeldragt: 'Så er det nu! Kirsten fra Cybersikkerhedstilsynet er ankommet ved Hovedindgangen. "
                "Hun er berygtet for at tjekke både netværkssegmentering, forensiske beviser og backup-procedurer. "
                "Gå ud og byd hende velkommen – du har styr på det!'"
            )

        return "Hans McDonald: 'Kaffemaskinen brygger stadig, og anlægget spinder som en mis. Godt arbejde!'"

    def get_anecdote(self) -> str:
        anecdotes = [
            "Hans mindes: 'Tilbage i 1999 kørte vi udelukkende med RS-485 og serielle kabler. Dengang kunne ingen hacke os udefra, "
            "medmindre de fysisk kravlede over hegnet med en skruetrækker i hånden. Nu om dage har alt en IP-adresse – selv kaffemaskinen!'",
            
            "Hans ler tørt: 'Jeg kan huske en IT-konsulent for ti år siden, der kørte en aggressiv port-scanning på vores spildevands-PLC. "
            "CPU'en fik et chok, gik i STOP, og oversvømmede kælderen med 400 kubikmeter råslam. Han lærte på den hårde måde, "
            "at OT ikke bare er almindelig kontor-IT!'",
            
            "Hans peger på en metalplade på væggen: 'Den gyldne regel i IEC 62443 hedder Zoner & Conduits. "
            "Man blander aldrig processtyring (Level 1) sammen med kontor-e-mails (Level 4). Gør man det, lukker tilsynet biksen på stedet.'",
            
            "Hans tager en slurk kaffe: 'Husk altid: En rigtig automationsteknolog stoler aldrig på 'Security through Obscurity'. "
            "At en angriber ikke kender IP-adressen på forhånd, stopper dem i præcis tre sekunder med Wireshark!'",
        ]
        return random.choice(anecdotes)

    def get_topic_response(self, topic: str) -> str:
        norm = topic.lower().strip()
        if "historie" in norm or "anlæg" in norm or "vandværk" in norm:
            return (
                "Hans fortæller: 'Nordic H2O Utility leverer rent drikkevand til 180.000 borgere. "
                "Vi har 3 dybdeboringer, 2 trykforøger-stationer og over 450 km distributionsrør. "
                "Hvis vores pumper stopper i mere end 4 timer, falder trykket i byens brandhaner, og hospitalet mangler vand!'"
            )
        if "montør" in norm or "person" in norm or "mistænkelig" in norm:
            return (
                "Hans skuler: 'Sidste tirsdag havde vi et eksternt pumpe-servicefirma på besøg. "
                "Montøren gik rundt med en rygsæk og spurgte påfaldende meget ind til vores switch-kabling og IP-ranges. "
                "Jeg har en stærk mistanke om, at det var ham, der tapede den sorte boks fast i kabelbakken!'"
            )
        if "råd" in norm or "hjælp" in norm or "tip" in norm:
            return (
                "Hans' tekniske råd: 'Brug altid Wireshark før du rører ved noget! Identificér modpartens MAC og IP. "
                "Når du skal sikre nettet, så brug SCALANCE hardwaren med VLAN og Deep Packet Inspection. "
                "Og husk: Når du konfiskerer mistænkeligt udstyr, så smid det ALDRIG i skraldespanden – put det i Faraday-posen!'"
            )
        if "kaffe" in norm:
            return "Hans smiler bredt: 'Kaffen i kontrolrummet er friskbrygget på mørkristede bønner. En tekniker uden kaffe er som en PLC uden strøm!'"
        
        return "Hans nikker eftertænksomt: 'Det er et godt spørgsmål. Kig dig omkring i zonen og brug din terminal!'"
