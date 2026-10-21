"""Hans McDonald (Senior Driftstekniker) - Dynamic Dialogue Engine with Situational Memory & Interrogation."""

from __future__ import annotations

import random
from typing import Any


class HansDialogue:
    """Manages Hans McDonald's situational responses, emotional states, OT anecdotes, and suspect interrogation."""

    def __init__(self) -> None:
        self.talk_count = 0
        self.interrogation_history: set[str] = set()
        self.remembered_mistakes: set[str] = set()
        self.remembered_praise: set[str] = set()

    def get_greeting(self, engine: Any) -> str:
        self.talk_count += 1
        flags = getattr(engine, "flags", set())
        ch = getattr(engine, "chapter", 1)
        metrics = getattr(engine, "metrics", None)
        tillid = metrics.tillid if metrics else 50

        # Memory tracking of player actions
        if getattr(engine, "breaker_tripped", False):
            self.remembered_mistakes.add("breaker_tripped")
        if getattr(engine, "scada_blind", False):
            self.remembered_mistakes.add("scada_blind")
        if getattr(engine, "plc_defect_stop", False):
            self.remembered_mistakes.add("plc_defect_stop")
        if "backup-taken" in flags:
            self.remembered_praise.add("backup_taken")
        if "pi-removed" in flags:
            self.remembered_praise.add("pi_removed")

        # 1. Acute emergency reactions (High emotional intensity)
        if getattr(engine, "breaker_tripped", False):
            return (
                "Hans taber kaffekoppen mod betongulvet: 'Hørte du det brag?! K1-sikringen i Hoved-el-tavlen slog fra! "
                "Det var et klassisk hydraulisk vandslag! Nogen må have hevet stikket til frekvensomformeren midt under fuld last. "
                "Skynd dig over til El-tavlen og nulstil relæet, før motorviklingerne tager permanent skade!'"
            )

        if getattr(engine, "scada_blind", False):
            return (
                "Hans råber febrilsk over radioen: 'Hov hov! Kontrolrummet melder over radioen, at SCADA er helt sort for Pumpe 2! "
                "Du har blokeret port 502 eller droppet FC 06 uden en allow-regel for FC 03! "
                "I procesanlæg kan vi ikke køre i blinde! Ret firewall-reglen så WinCC kan læse måleværdierne!'"
            )

        if getattr(engine, "plc_defect_stop", False):
            return (
                "Hans tager sig til hovedet med rystende hænder: 'Det er mareridtet i Hoved-el-tavlen! S7-1500 PLC'en står i DEFECTIVE STOP! "
                "Fejlkode 0x4542 betyder CRC-korruption i sikkerhedsblokkene. Rør aldrig ved en PLC uden offline backup i hånden! "
                "Find dit USB-stik frem og få genskabt DB1!'"
            )

        if getattr(engine, "cavitation_deadline_active", False):
            return (
                "Hans overdøves næsten af et infernalsk metallisk hyl: 'Hører du det?! Det er kavitation! Når modtrykket forsvinder, "
                "imploderer mikroskopiske dampbobler mod skovlhjulene som små sprængladninger! "
                "Få fat i den SCALANCE switch og slut PROFINET MRP-ringen før pumperne er skrot!'"
            )

        if getattr(engine, "pump_deadline_active", False):
            return (
                "Hans peger nervøst mod Pumpehuset: 'Hører du sirenen? Manometeret står og hopper faretruende over 140 Bar! "
                "Rørene holder ikke til 150 Bar. Kør tshark og find ud af hvem der oversvømmer VFD'en!'"
            )

        # 2. Trust-based tone & commentary on history
        trust_prefix = ""
        if tillid >= 75:
            trust_prefix = "Hans smiler bredt og byder på frisk kaffe: 'Det er en fornøjelse at arbejde sammen med en teknolog, der tænker før de handler. '"
        elif tillid <= 35:
            trust_prefix = "Hans kigger bekymret på dig og holder kaffekoppen tæt ind til brystet: 'Jeg håber virkelig du ved hvad du gør, makker... mit anlæg har overlevet 30 år uden nedbrud indtil nu. '"

        # 3. Chapter-specific contextual guidance
        if ch == 1:
            return (
                f"{trust_prefix}"
                "Hans: 'Pumpe 2 opfører sig fuldstændig utilregneligt. Manometeret ryster, men SCADA viser intet. "
                "Gå over i Pumpehuset og kobl din laptop på. Du kan spørge mig om alt undervejs – f.eks. 'spørg hans om morten' eller 'spørg hans om lars'.'"
            )

        if ch == 2:
            if "pi-removed" not in flags:
                return (
                    f"{trust_prefix}"
                    "Hans hvisker dæmpet: 'De Festo-ventiler danser rundt som til en folkefest. "
                    "Vores lærling mente han så et blåt netværkskabel, der forsvandt op under kabelbakken bag ventilstativerne. "
                    "Det kabel findes ikke i vores P&ID-tegninger! Undersøg den kabelbakke grundigt!'"
                )
            return (
                f"{trust_prefix}"
                "Hans nikker anerkendende: 'Godt du fik pillet den rogue Raspberry Pi fra og sikret den i posen. "
                "Nu skal vi have erstattet den gamle D-Link switch med den industrielle SCALANCE XB-200 med MRP-ringstyring.'"
            )

        if ch == 3:
            return (
                f"{trust_prefix}"
                "Hans klør sig i skægget: 'S7-1500 PLC'en er hjertet i hele anlægget. "
                "Husk hvad jeg sagde: En god automationsteknolog starter altid med en frisk backup på USB før noget overføres! "
                "Dernæst logger du ind via TIA Portal og lukker for ubeskyttet PUT/GET kommunikation!'"
            )

        if ch == 4:
            return (
                f"{trust_prefix}"
                "Hans kigger ud over kontrolrummet: 'Kontrolrummet er vores IDMZ. "
                "Der må ALDRIG være direkte forbindelse fra internettet ind til feltbussen. "
                "Kig bag SCADA-racket – der hænger en 4G-router som en ekstern montør 'glemte' under nedlukningen!'"
            )

        if ch == 5:
            return (
                f"{trust_prefix}"
                "Hans retter på sit kedeldragt med stolthed: 'Så er det nu! Kirsten fra Cybersikkerhedstilsynet er ankommet ved Hovedindgangen. "
                "Hun er skarp som en barberkniv og tjekker alt: segmentering, forensiske beviser og backup-procedurer. "
                "Gå ud og fremlæg dokumentationen – vi har gjort vores forarbejde ordentligt!'"
            )

        return f"{trust_prefix}Hans McDonald: 'Kaffemaskinen brygger stadig, og anlægget spinder som en mis. Godt arbejde!'"

    def interrogate(self, engine: Any, topic: str) -> str:
        """Handle targeted detective questioning about suspects, history, or plant equipment."""
        norm = topic.lower().strip()
        self.interrogation_history.add(norm)
        investigation = getattr(engine, "investigation", None)

        if any(k in norm for k in {"morten", "hydropump", "leverandør", "pumpefirma", "pumpe-mand"}):
            if investigation:
                engine.record_clue("spor_morten_rapport")
            return (
                "Hans sætter kaffekoppen med et klask og rynker brynene:\n"
                "\"Morten fra Hydropump Nordic? Ja, han var her tirsdag eftermiddag for at 'optimere flowet' på pumpe 2.\n"
                "Han havde sin egen bærbar med og koblede sig direkte på frekvensomformerens RS-485 port og netværket.\n"
                "Han virkede underligt stresset og havde travlt med at komme ud af døren før fyraften.\n"
                "Jeg spurgte ham om en servicerapport, men han mumlede noget om, at han ville maile den fra kontoret.\n"
                "Mærkeligt nok begyndte de voldsomme trykudsving på Pumpe 2 samme aften... Tror du, han har rodet med Modbus-registrene?\""
            )

        if any(k in norm for k in {"lars", "fyret", "tidligere tekniker", "automationstekniker", "forgænger"}):
            if investigation:
                engine.record_clue("spor_usb_backup")
            return (
                "Hans sukker dybt og ser sig over skulderen:\n"
                "\"Lars Kofoed... Han var vores skarpe automationstekniker i tre år, indtil ledelsen fyrede ham for to måneder siden.\n"
                "Det var en grim fyring – Lars mente, han havde 200 timers ubetalt overarbejde til gode, og han råbte, at 'værket ikke kunne køre en uge uden ham'.\n"
                "Lars kender samtlige adgangskoder, IP-adresser og datablokke i S7-1500 PLC'en.\n"
                "Faktisk var det Lars, der installerede den gamle D-Link switch og konfigurerede de oprindelige TIA-projekter.\n"
                "Hvis nogen ville plante en hemmelig Raspberry Pi eller overskrive DB1 med en byte-bombe, så har Lars evnerne til det!\""
            )

        if any(k in norm for k in {"kim", "operatør", "nathold", "nattevagt"}):
            if investigation:
                engine.record_clue("spor_kim_nattevagt")
            return (
                "Hans griner lidt skævt:\n"
                "\"Kim på natholdet? Kim er en fin fyr, men magelig! Han har brokket sig i årevis over, at han skal køre 30 km herind midt om natten\n"
                "bare for at kvittere en triviel højniveau-alarm på en bundfældningstank.\n"
                "Han bad ledelsen om en officiel VPN-forbindelse, men IT sagde nej af sikkerhedshensyn.\n"
                "Jeg har hørt rygter om, at han fandt en Teltonika 4G-router i skrotkassen og satte sit eget private SIM-kort i den...\n"
                "Det er ulovlig Shadow-IT, men Kim gjorde det nok af dovenskab, ikke for at sabotere os!\""
            )

        if any(k in norm for k in {"4g", "router", "teltonika", "dongle", "bagdør"}):
            if investigation:
                engine.record_clue("spor_4g_dongle")
            return (
                "Hans nikker energisk:\n"
                "\"Ja! Den Teltonika RUT950 router, der sidder bag SCADA-racket i Kontrolrummet.\n"
                "Den er ikke godkendt i vores netværksarkitektur. Den skaber en uovervåget tunnel direkte udenom vores firewall.\n"
                "Hvis en angriber eller Kim logger ind over 4G-nettet, er de direkte inde på vores Level 3 SCADA-netværk! Træk stikket til den!\""
            )

        if any(k in norm for k in {"pi", "raspberry", "sort boks", "gaffa", "kabelbakke"}):
            if investigation:
                engine.record_clue("spor_sort_boks")
            return (
                "Hans peger med fingeren:\n"
                "\"Den optapede sorte boks i kabelbakken på Ventil-øen er et decideret hardware-implantat!\n"
                "En Raspberry Pi med PoE-splitter sat i port 3 på den gamle switch. Nogen har fysisk monteret den dér for at omgå perimeteren.\n"
                "Det beviser, at vi enten har haft en insider i huset, eller at en leverandør har haft frie hænder uden opsyn!\""
            )

        if any(k in norm for k in {"stuxnet", "historie", "anekdote", "erfaring", "gamle dage"}):
            return self.get_anecdote()

        if any(k in norm for k in {"nis2", "kirsten", "audit", "tilsyn", "artikel 21"}):
            return (
                "Hans retter brillerne:\n"
                "\"Kirsten er jurist og revisor ind til benet. Hun er ligeglad med gode intentioner – hun vil se logfiler og beviser!\n"
                "Under NIS2 Artikel 21 skal vi kunne dokumentere hændelseshåndtering, forsyningskædesikkerhed og backup.\n"
                "Og glem ikke 24-timers fristen for tidlig advarsel i Artikel 23 – hvis vi ikke har meldt hændelsen til CSIRT, er vi færdige!\""
            )

        if any(k in norm for k in {"modbus", "fc03", "fc 03", "fc06", "fc 06"}):
            return (
                "Hans forklarer pædagogisk:\n"
                "\"Modbus TCP er fra 1979 og har nul sikkerhed. Function Code 03 er 'Read Holding Registers' – det bruger SCADA til at se tryk og flow.\n"
                "Function Code 06 er 'Write Single Register' – det er det angriberen bruger til at tvinge VFD'en op på 120 Hz!\n"
                "Når du sætter firewallen op, SKAL du tillade FC 03 og blokere FC 06. Glemmer du FC 03, kan SCADA ikke se noget, og anlægget går i timeout!\""
            )

        return (
            f"Hans lytter opmærksomt til dit spørgsmål om '{topic}':\n"
            "\"Det er en interessant vinkel, men hold fokus på anlæggets akutte symptomer.\n"
            "Brug din terminal, kør tshark for at fange pakker, eller undersøg komponenterne i rummet!\""
        )

    def get_anecdote(self) -> str:
        anecdotes = [
            "Hans mindes med et skævt smil: 'Tilbage i 2010, da Stuxnet ramte centrifugerne i Iran, grinede IT-folkene og sagde, at PLC-sabotage var ren science fiction. "
            "To uger senere opdagede vi, at vores egne S7-300 PLC'er kørte med standardkodeordet 'admin123' og tillod enhver på lokalnettet at skrive i DB-blokkene. "
            "Siden da har jeg lært: Hvis en port er åben på OT, bliver den udnyttet før eller siden!'",

            "Hans ler tørt: 'Jeg husker en smart konsulent for ti år siden, der kørte et automatiseret sårbarhedsscan mod vores pumpe-PLC. "
            "CPU'en fik et chok over de mange malformede TCP-syn pakker, gik i STOP, og spildevandskælderen blev oversvømmet med 400 kubikmeter råslam. "
            "Han lærte på den hårde måde, at OT-systemer ikke tåler brute-force IT-værktøjer!'",

            "Hans peger på en metalplade på væggen: 'Den gyldne regel i IEC 62443 hedder Zoner & Conduits. "
            "Man blander ALDRIG processtyring (Purdue Level 1) sammen med kontor-e-mails (Level 4). "
            "Gør man det, kan en enkelt phishing-mail på direktørens laptop i princippet stoppe byens vandforsyning.'",

            "Hans tager en slurk kaffe: 'Husk altid: En god automationsteknolog stoler aldrig på 'Security through Obscurity'. "
            "At en angriber ikke kender IP-adressen på forhånd, stopper dem i præcis fire sekunder med Wireshark eller tshark!'"
        ]
        return random.choice(anecdotes)

    def get_final_verdict_reaction(self, metrics: Any, prime_suspect_id: str | None) -> str:
        """Hans' concluding speech based on Drift, Tillid, and who was caught."""
        lines = []
        drift = getattr(metrics, "drift", 50)
        tillid = getattr(metrics, "tillid", 50)

        lines.append("\n☕ [HANS MCDONALDS DRIFTSDEBRIEFING]:")
        if drift >= 75:
            lines.append(
                f"Hans slår ud med armene og smiler bredt:\n"
                f"\"🔧 DRIFT ({drift}%): Byens vandforsyning står klippefast! Trykket på Pumpe 2 ligger snorlige på 42.0 Bar, "
                f"kavitationen blev kvalt i fødslen, og vi har ikke haft et eneste sekunds udfald for borgerne.\""
            )
        else:
            lines.append(
                f"Hans ryster på hovedet med bekymret mine:\n"
                f"\"🔧 DRIFT ({drift}%): Pumperne og rørledningerne tog hårdt skade af de hydrauliske stød og afbrydelser. "
                f"Vi må have pumperne adskilt og lejerne efterset i næste uge.\""
            )

        if tillid >= 75:
            lines.append(
                f"\n🤝 TILLID & PARTNERSKAB ({tillid}%):\n"
                f"\"Jeg indrømmer blankt, jeg var skeptisk da du trådte ind ad døren med din laptop. Sikkerhedsfolk plejer bare at "
                f"trække stik og gøre hverdagen besværlig for os i driften. Men du lyttede til os, der kender anlægget, "
                f"og du lærte os hvorfor en conduit og et certifikat redder os mod cyberangreb. "
                f"Tag min gamle 'Nordic H2O' messing-nøglering her – den har åbnet tavlerne siden '98. Du er altid velkommen på værket!\""
            )
        elif tillid >= 50:
            lines.append(
                f"\n🤝 TILLID & PARTNERSKAB ({tillid}%):\n"
                f"\"Vi fik da anlægget igennem ugen, makker. Samarbejdet kradsede lidt indimellem, men vi nåede i mål. "
                f"Næste gang må du godt advare os, inden du piller ved netværkskablerne.\""
            )
        else:
            lines.append(
                f"\n🤝 TILLID & PARTNERSKAB ({tillid}%):\n"
                f"\"Det har været en hård uge for driften. Vi følte os mere som mistænkte end som kollegaer. "
                f"Cybersikkerhed må aldrig blive en krig mod dem, der holder fabrikken kørende.\""
            )

        if prime_suspect_id == "lars_ex_tekniker":
            lines.append(
                f"\n🎯 OM GERNINSMANDEN (LARS KOFOED):\n"
                f"\"Stakkels Lars... Han var sgu en dygtig automationstekniker, men bitterhed og såret stolthed gjorde ham blind. "
                f"Godt du fik stoppet ham før han sprængte vores rørnetværk i stumper og stykker.\""
            )

        return "\n".join(lines)
