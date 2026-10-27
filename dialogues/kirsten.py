"""Revisor Kirsten (Miljø- og Cybersikkerhedstilsynet) - Audit Dialogue & NIS2 Evaluation."""

from __future__ import annotations

from typing import Any


class KirstenDialogue:
    """Manages Auditor Kirsten's rigorous regulatory oversight, interim audits, and legal pressure."""

    def __init__(self) -> None:
        self.contact_count = 0

    def get_interim_audit(self, engine: Any) -> str:
        """Provide a demanding midterm compliance assessment during the working week."""
        self.contact_count += 1
        day = getattr(engine, "simulated_day", 1)
        hour = getattr(engine, "simulated_hour", 1)
        incident = getattr(engine, "incident", None)
        forensics = getattr(engine, "forensics", None)
        metrics = getattr(engine, "metrics", None)
        early_warning = incident.early_warning_sent if incident else False

        lines = [
            f"\n📞 [OPKALD TIL MILJØ- OG CYBERSIKKERHEDSTILSYNET - REVISOR KIRSTEN]:",
            f"Kirsten svarer efter præcis to ringetoner med en tør, formel stemme:",
            f"\"Goddag. Tilsynet her. Du taler med ledende auditor Kirsten.\"",
            f"\"I befinder jer på Dag {day}, time {hour} af jeres varslede ugeperiode.\"",
            "",
            "📋 TILSYSNETS FORELØBIGE RISIKOVURDERING:",
        ]

        # 1. Early Warning check
        if early_warning:
            lines.append("  • [NIS2 ARTIKEL 23]: ✅ Lovpligtig 24-timers Early Warning er registreret i CSIRT-databasen.")
        else:
            lines.append(
                "  • [NIS2 ARTIKEL 23]: 🚨 ADVARSEL! Ingen 'Tidlig Advarsel' modtaget endnu! "
                "Hvis en væsentlig hændelse ikke anmeldes inden 24 timer fra detektering, udløser det automatisk anmærkning og bødeforlæg!"
            )

        # 2. Forensic handling check
        pi_state = forensics.pi_handling_state if forensics else "unhandled"
        if pi_state == "secured":
            lines.append("  • [ARTIKEL 21.2.b]: ✅ Sikring af beslaglagt hardware i Faraday-pose og SHA-256 integritet godkendt.")
        elif pi_state == "trashed":
            lines.append("  • [ARTIKEL 21.2.b]: ❌ KRITISK OVERTRÆDELSE! Destruktion af hardware-bevis i skraldespand er strafbart tab af bevis.")
        elif pi_state in {"reused", "infected"}:
            lines.append("  • [ARTIKEL 21.2.b]: ❌ KRITISK OVERTRÆDELSE! Kompromitteret udstyr er genbrugt eller tilsluttet privat udstyr.")
        else:
            lines.append("  • [ARTIKEL 21.2.b]: ⚠️ Eventuelt mistænkeligt hardware skal sikres forensisk og forsegles ubrudt.")

        # 3. Compliance metric
        if metrics:
            comp = metrics.compliance
            if comp >= 75:
                lines.append(f"  • Samlet efterlevelsesgrad: [{comp}%] - Tilfredsstillende fremdrift mod certificering.")
            elif comp >= 50:
                lines.append(f"  • Samlet efterlevelsesgrad: [{comp}%] - Utilstrækkelig dokumentation. I risikerer påbud ved ugeslut.")
            else:
                lines.append(f"  • Samlet efterlevelsesgrad: [{comp}%] - KRITISK LAV. Driftstilladelsen vil blive inddraget på fredag.")

        lines.extend([
            "",
            "Kirsten afslutter skarpt:",
            "\"I procesanlæg er gode intentioner ligegyldige. Vi kigger udelukkende på verificerbar dokumentation,",
            "forensisk beviskæde og overholdelse af tidsfrister. Vi ses til den afsluttende revision på Dag 5!\"",
        ])
        return "\n".join(lines)

    def interrogate(self, engine: Any, topic: str) -> str:
        """Answer specific regulatory inquiries regarding NIS2, sanctions, and evidence requirements."""
        norm = topic.lower().strip()

        if any(k in norm for k in {"artikel 23", "early warning", "advarsel", "frist", "24 timer"}):
            return (
                "Kirsten belærer dig formelt:\n"
                "\"NIS2 Artikel 23.2 fastsætter en ufravigelig frist: En 'tidlig advarsel' skal indgives til CSIRT / Tilsynet\n"
                "uden unødig forsinkelse og under alle omstændigheder inden for 24 timer efter, at den væsentlige hændelse blev opdaget.\n"
                "Advarslen skal angive, om hændelsen formodes at skyldes ulovlige eller ondsindede handlinger,\n"
                "eller om den kan have grænseoverskridende virkninger. Brug kommandoen 'indberet hændelse' før fristen udløber!\""
            )

        if any(k in norm for k in {"artikel 21", "foranstaltninger", "krav", "standard", "iec 62443"}):
            return (
                "Kirsten bladrer i EU-direktivet:\n"
                "\"NIS2 Artikel 21 pålægger ledelsen at gennemføre passende og forholdsmæssige tekniske foranstaltninger:\n"
                "  1. Risikovurderinger og sikkerhedspolitikker for informationssystemer.\n"
                "  2. Hændelseshåndtering (forebyggelse, opdagelse og reaktion jf. NIST SP 800-61).\n"
                "  3. Driftskontinuitet (backup og nødstrømsplaner jf. Artikel 21.2.c).\n"
                "  4. Forsyningskædesikkerhed (leverandørkontrol af f.eks. eksterne pumpe-teknikere).\n"
                "  5. Netværkssikkerhed og kryptering (IEC 62443 zoner og conduits samt Basic256Sha256 i OPC UA).\n"
                "Hvis ét af disse punkter fejler under auditten, falder det samlede regnskab til jorden!\""
            )

        if any(k in norm for k in {"bevis", "forensik", "faraday", "chain of custody", "sha-256", "hash"}):
            return (
                "Kirsten ser strengt på dig:\n"
                "\"I henhold til strafferetsplejen og NIS2 Artikel 21.2.b er digital evidens ekstremt flygtig.\n"
                "Hvis I beslaglægger en rogue enhed – som f.eks. en Raspberry Pi i en kabelbakke – skal den straks\n"
                "placeres i en antistatisk Faraday-pose for at afskære trådløse radiosignaler (Bluetooth/Wi-Fi).\n"
                "Der skal straks udregnes en kryptografisk SHA-256 hash af hukommelsen, og posen skal forsegles med plomberingsnummer.\n"
                "Smid aldrig hardware i skraldespanden eller sæt SD-kortet i jeres private laptop! Gør I det, er beviset kontamineret!\""
            )

        if any(k in norm for k in {"bøde", "straf", "sanktion", "ledelse", "ansvar"}):
            return (
                "Kirsten hæver stemmen:\n"
                "\"Under NIS2 er ledelsesansvaret personligt (Artikel 20).\n"
                "Bøderne for væsentlige enheder kan andrage op til 10 millioner euro eller 2% af den samlede globale omsætning.\n"
                "Dertil kommer, at Tilsynet kan nedlægge midlertidigt forbud mod, at ledende medarbejdere udøver ledelsesfunktioner.\n"
                "Det er derfor, direktør Jens Majer sveder tran! Gør jeres arbejde ordentligt!\""
            )

        return (
            f"Kirsten noterer dit spørgsmål om '{topic}' i sin journal:\n"
            "\"Tilsynet yder ikke rådgivning om driftstekniske detaljer. Vi måler jer udelukkende på compliance.\n"
            "Overhold tidsfristerne, luk bagdørene, og fremlæg dokumentationen på fredag!\""
        )

    def get_audit_intro(self, player_name: str) -> str:
        return (
            f"Kirsten tager sine læsebriller på og slår op i sit clipboard:\n"
            f"\"Goddag, {player_name}. Jeg er Kirsten fra Miljø- og Cybersikkerhedstilsynet.\n"
            f"Nordic H2O Utility er klassificeret som en 'Væsentlig Enhed' under NIS2-direktivet (EU 2022/2555).\n"
            f"I dag skal jeg kontrollere, om anlægget opfylder de 10 obligatoriske risikostyringskrav i Artikel 21 "
            f"samt de tekniske krav i IEC 62443 standarden.\n"
            f"Lad mig se din dokumentation og gennemgå anlæggets zoner punkt for punkt.\""
        )

    def format_verdict(self, passed: bool, score: int, remarks: list[str]) -> str:
        lines = []
        if passed:
            lines.append(f"\n🏆 [AUDIT BESTÅET! CERTIFICERING TILDELT - SCORE: {score}/100 POINT]:")
            lines.append("Kirsten nikker anerkendende og sætter sit officielle stempel:")
            lines.append(
                f"\"Fremragende arbejde, konsulent! Du har demonstreret dyb teknisk forståelse for "
                f"både OT-netværkssikkerhed, IEC 62443 zoner og conduits, samt NIS2 Artikel 21.\n"
                f"Driftstilladelsen til Nordic H2O Utility er hermed forlænget for de næste tre år!\""
            )
        else:
            lines.append(f"\n❌ [AUDIT DUMPET - DRIFTSTILLADELSE INDDRAGET - SCORE: {score}/100 POINT]:")
            lines.append("Kirsten ryster alvorligt på hovedet og trækker den røde pen frem:")
            lines.append(
                f"\"Det her er ikke acceptabelt. Der er konstateret kritiske afvigelser fra NIS2 Artikel 21.\n"
                f"Et vandværk i kritisk infrastruktur kan ikke drives med disse sikkerhedsmæssige huller.\n"
                f"Følgende mangler skal udbedres omgående f.s.v. anlægget ikke skal påbydes standsning:\""
            )

        lines.append("\nKIRSTENS AUDIT-BEMÆRKNINGER:")
        for r in remarks:
            lines.append(f"  • {r}")

        return "\n".join(lines)

    def format_final_verdict(
        self,
        passed: bool,
        score: int,
        metrics: Any,
        remarks: list[str],
        prime_suspect_id: str | None,
        true_culprit_id: str = "lars_ex_tekniker",
    ) -> str:
        """Kirsten's comprehensive regulatory decree evaluating all 4 dimensions and the investigation."""
        lines = []
        drift = getattr(metrics, "drift", 50)
        sikkerhed = getattr(metrics, "sikkerhed", 50)
        compliance = getattr(metrics, "compliance", 50)
        tillid = getattr(metrics, "tillid", 50)

        culprit_labels = {
            "lars_ex_tekniker": "Lars Kofoed (Tidligere automationstekniker)",
            "morten_pumper": "Morten Vestergaard (Hydropump Nordic A/S)",
            "apt_shadowh2o": "ShadowH2O / DarkVolt Syndikatet (APT)",
            "kim_operatoer": "Kim Dahl (Intern procesoperatør)",
        }
        true_label = culprit_labels.get(true_culprit_id, true_culprit_id)

        lines.extend([
            "================================================================================",
            "        ⚖️  MILJØ- OG CYBERSIKKERHEDSTILSYNET – AFSLUTTENDE NIS2 AUDIT-DEKRET   ",
            "================================================================================",
            f"Væsentlig Enhed: Nordic H2O Utility A/S (Drikkevandsforsyning)",
            f"Tilsynsførende:   Chefinspektør Kirsten, Cybersikkerhedstilsynet",
            f"Audit-score:     {score} / 100 point  (Krav til godkendelse: min. 80 point)",
            "--------------------------------------------------------------------------------",
            "📊 EVALUERING AF ANLÆGGETS 4 HOVEDMETRIKKER:",
            f"  • 🔧 Drift:      [{drift:3d}%] - {'✅ Oppetid & vandforsyning sikret' if drift >= 75 else '⚠️ Driftstab eller kavitationsslitage'}",
            f"  • 🛡️ Sikkerhed:  [{sikkerhed:3d}%] - {'✅ IEC 62443 zoner & conduits hærdet (SL-2)' if sikkerhed >= 75 else '⚠️ Åbne sårbarheder i zonerne'}",
            f"  • 📜 Compliance: [{compliance:3d}%] - {'✅ NIS2 Artikel 21/23 procedurer fuldt overholdt' if compliance >= 75 else '⚠️ Mangelfuld dokumentation eller fristoverskridelse'}",
            f"  • 🤝 Tillid:     [{tillid:3d}%] - {'✅ Stærkt tværfagligt samarbejde med driften' if tillid >= 75 else '⚠️ Samarbejdsvanskeligheder under krisestyringen'}",
            "--------------------------------------------------------------------------------",
            "🔍 EFTERFORSKNINGENS KONKLUSION:",
        ])

        if prime_suspect_id == true_culprit_id:
            lines.append(f"  • Gerningsmand:  {true_label} -> ✅ KORREKT IDENTIFICERET!")
            lines.append("    Status:        Sagen er overdraget til Rigspolitiets NC3 med beslaglagt bevismateriale.")
        elif prime_suspect_id:
            lines.append(f"  • Gerningsmand:  {prime_suspect_id} -> ⚠️ VILDLEDT ELLER UFULDSTÆNDIG HYPOTESE.")
            lines.append(f"    Status:        Den reelle bagmand ({true_label}) undslap i første omgang.")
        else:
            lines.append("  • Gerningsmand:  INGEN HOVEDMISTÆNKT UDPEGET.")
            lines.append("    Status:        Efterforskningen mangler formel anklage.")

        lines.extend([
            "--------------------------------------------------------------------------------",
            "📋 KIRSTENS REVISIONSPUNKTER (NIS2 ARTIKEL 21 & 23):",
        ])
        for r in remarks:
            icon = "✅" if not any(w in r for w in {"Mangler", "Manglende", "KRITISK", "FEJL", "fejl", "står", "blindet"}) else "❌"
            lines.append(f"  {icon} {r}")

        lines.append("--------------------------------------------------------------------------------")

        if passed and score >= 90 and drift >= 70 and sikkerhed >= 70:
            lines.extend([
                "🏆 [RESULTAT: AKKREDITERET MED UDMÆRKELSE - GULDSTANDARD]:",
                "Kirsten letter på læsebrillerne og trykker sit grønne certifikatstempel:",
                "\"Et forbilledligt stykke arbejde! Du har demonstreret, hvordan fremtidens automationsingeniører",
                "forener dyb OT-procesforståelse (bits & bar) med kompromisløs cybersikkerhed og retsmedicinsk omhu.",
                "Nordic H2O Utility tildeles fuld 3-årig NIS2 driftstilladelse uden anmærkninger!\"",
            ])
        elif passed:
            lines.extend([
                "🏆 [RESULTAT: AUDIT BESTÅET - DRIFTSTILLADELSE FORLÆNGET]:",
                "Kirsten sætter sit godkendelsesstempel:",
                "\"Kravene i NIS2 Artikel 21 er opfyldt på et acceptabelt niveau. Værket kan fortsætte driften.",
                "Følg op på de resterende anmærkninger inden næste kvartalsgennemgang.\"",
            ])
        else:
            lines.extend([
                "❌ [RESULTAT: AUDIT DUMPET - DRIFTSTILLADELSE INDDRAGET]:",
                "Kirsten ryster alvorligt på hovedet og trækker det røde forseglingsbånd frem:",
                "\"Dette anlæg overholder ikke minimumskravene i NIS2 Artikel 21. Risikoen for byens drikkevand",
                "er uacceptabel høj. Der udstedes straks standsningspåbud jf. NIS2 Artikel 32!\"",
            ])

        lines.append("================================================================================")
        return "\n".join(lines)
