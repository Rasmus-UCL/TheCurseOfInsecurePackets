"""Main entry point for The Curse of Insecure Packets.

The graphical client is the default. Use ``--cli`` for the terminal version.
"""

from __future__ import annotations

import os
import sys

from engine import GameEngine


def print_background() -> None:
    """Display the plant background story, Purdue model and NIS2 context."""
    print("\n" + "=" * 70)
    print("      OM SPILLET, PURDUE-MODELLEN & NIS2 CYBERSIKKERHED")
    print("=" * 70)
    print("""
1. BAGGRUND: VANDVÆRKET NORDIC H2O UTILITY
Nordic H2O Utility forsyner 85.000 borgere med rent drikkevand. De seneste uger
har SCADA-systemet oplevet uforklarlige trykfald, uautoriseret fjernadgang og
mystisk netværkstrafik på tværs af produktionszonerne. Anlæggets zoner rammes nu
af koordinerede tekniske cyberangreb, og Miljø- og Cybersikkerhedstilsynet ved
Revisor Kirsten har indledt et uanmeldt 5-dages NIS2-tilsyn med trussel om
10 mio. EUR i bøde.

2. PURDUE MODELLEN & IEC 62443-3-2 ZONER & CONDUITS
Anlæggets OT-arkitektur er opbygget jf. Purdue Enterprise Reference Architecture:
  • Level 0 (Fysisk proces):   Pumper, ventiler, tryktransmittere og flowmålere.
  • Level 1 (Styring):         Siemens S7-1500 PLC'er, SINAMICS VFD, Festo Ventil-ø.
  • Level 2 (Områdestyring):   Lokale HMI touchskærme, SCALANCE managed switches.
  • Level 3 (Driftsledelse):   SCADA WinCC servere, historikere, ingeniør-stationer.
  • Level 3.5 (IDMZ):          Industriel DMZ med firewalls, jump hosts og PKI Truststore.
  • Level 4 (Enterprise):      Kontor-IT, ERP og eksterne leverandør-forbindelser.

3. NIS2-DIREKTIVET (ARTIKEL 21 & 23)
Som væsentlig samfundskritisk enhed underlagt NIS2 skal forsyningen overholde:
  • Artikel 21: Risikostyringsforanstaltninger (hærdning, adgangskontrol, segmentering).
  • Artikel 23: Obligatorisk hændelsesrapportering (24t tidlig advarsel, 72t rapport).
  • Sanktioner: Bøder på op til 10 mio. EUR eller 2% af den globale koncernomsætning.

4. DE 4 HOVEDMETRIKKER
  • 🔧 DRIFT (0-100%):      Vandværkets driftsoppetid og forsyningssikkerhed.
  • 🛡️ SIKKERHED (0-100%):  Netværkets modstandsdygtighed og hærdning.
  • 📜 COMPLIANCE (0-100%): NIS2-dokumentation, bevisintegritet og revisionsstandarder.
  • 🤝 TILLID (0-100%):     Samarbejde med driftstekniker Hans McDonald og ledelsen.

5. GEM, INDLÆS & NAVIGATION
  • Gem dit spil: Tast 'gem' eller 'gem <navn>'.
  • Indlæs et spil: Tast 'hent' eller 'hent <navn>'.
  • Vend tilbage til Hovedmenuen: Tast 'hovedmenu' eller 'menu'.
""")
    input("Tryk Enter for at vende tilbage til Hovedmenuen...")


def run_cli() -> None:
    """Start the text client with main menu (Teach/Exam, Load, Background, Exit)."""
    while True:
        print("\n" + "=" * 70)
        print("          THE CURSE OF INSECURE PACKETS — HOVEDMENU")
        print("   Nordic H2O Utility Incident Cockpit (NIS2 / IEC 62443)")
        print("=" * 70)
        print("  1. 🎓 Start Nyt Spil (Teach Mode — Vejledning & faldgruber)")
        print("  2. 📝 Start Nyt Spil (Exam Mode — Skarp evaluering, ingen hints)")
        print("  3. 💾 Indlæs Gemt Spil (Hent spil fra 'saves/' mappen)")
        print("  4. 📖 Om Spillet & Baggrundshistorie (Purdue, NIS2 og scenarie)")
        print("  5. ❌ Afslut")
        print("=" * 70)

        choice = input("\nVælg et menupunkt [1-5]: ").strip()

        if choice in {"1", "2"}:
            game = GameEngine()
            game.game_mode = "teach" if choice == "1" else "exam"
            mode_name = "TEACH MODE (Undervisning)" if choice == "1" else "EXAM MODE (Eksamen)"
            print(f"\n[STARTER NY MISSION I {mode_name}]")
            name = input("Hvad hedder du? [Konsulent]: ").strip() or "Konsulent"
            education = input("Hvilken uddannelse kommer du fra? [Automationsteknolog]: ").strip() or "Automationsteknolog"
            game.start(name, education)
            print("\n💡 Skriv HJÆLP for kommandoer, GEM for at gemme, HOVEDMENU for at gå til menu.")
            while game.running:
                try:
                    cmd = input("\n> ")
                    game.handle_command(cmd)
                    if "return-to-menu" in game.flags:
                        game.flags.remove("return-to-menu")
                        break
                except (EOFError, KeyboardInterrupt):
                    print()
                    break

        elif choice == "3":
            game = GameEngine()
            saves = game.list_save_files()
            if not saves:
                print("\n⚠️ Ingen gemte spil fundet i 'saves/' mappen.")
                input("Tryk Enter for at vende tilbage...")
                continue

            print("\n💾 GEMTE SPIL I 'saves/':")
            for idx, s in enumerate(saves, start=1):
                m = s.get("metrics", {})
                print(f"  [{idx}] {s['filename']} — {s['player_name']} (Kap. {s['chapter']}/5, {s['game_mode'].upper()}) [{s['save_time']}]")
                print(f"      Drift: {m.get('drift', '--')}% | Sikkerhed: {m.get('sikkerhed', '--')}% | Compliance: {m.get('compliance', '--')}% | Tillid: {m.get('tillid', '--')}%")

            sel_str = input("\nVælg nummer for at indlæse (eller tryk Enter for at annullere): ").strip()
            if not sel_str.isdigit() or int(sel_str) < 1 or int(sel_str) > len(saves):
                continue

            target_save = saves[int(sel_str) - 1]
            ok, msg = game.load_state(target_save["filepath"])
            print(msg)
            if ok:
                game.describe_room()
                while game.running:
                    try:
                        cmd = input("\n> ")
                        game.handle_command(cmd)
                        if "return-to-menu" in game.flags:
                            game.flags.remove("return-to-menu")
                            break
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break

        elif choice == "4":
            print_background()

        elif choice in {"5", "q", "quit", "exit"}:
            print("\nTak for indsatsen hos Nordic H2O Utility. På gensyn!")
            break


def main() -> None:
    """Start the graphical client unless the CLI was explicitly requested."""
    if "--cli" in sys.argv:
        run_cli()
        return

    from gui import GameApp

    GameApp().mainloop()


if __name__ == "__main__":
    main()
