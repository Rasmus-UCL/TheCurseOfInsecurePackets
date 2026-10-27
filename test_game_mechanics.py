"""Comprehensive automated verification tests for The Curse of Insecure Packets."""

import os
import sys

from core.engine import GameEngine
from core.forensics import ForensicsManager
from core.incident import IncidentManager
from core.purdue import PURDUE_LEVELS
from core.terminal_engine import AutocompleteHelper, WiresharkSniffer
from devices import OpcUaDevice, PLCDevice, RoguePiDevice, SwitchDevice, VFDDevice
from dialogues import HansDialogue, KirstenDialogue
from rooms import ALL_ROOMS


def test_purdue_and_iec():
    print("Test 1: Purdue & IEC 62443 mapping...")
    assert len(PURDUE_LEVELS) >= 5
    assert "Level 1" in PURDUE_LEVELS[1.0].name
    assert PURDUE_LEVELS[3.5].level == 3.5
    print("  -> Passed.")


def test_sniffer_and_wireshark():
    print("Test 2: Wireshark sniffer & display filters...")
    sniffer = WiresharkSniffer()
    packets = sniffer.get_packets_for_zone("pumpehuset")
    assert len(packets) > 0
    modbus_pkts = [p for p in packets if p["proto"].lower() == "modbus"]
    assert len(modbus_pkts) > 0
    assert "Modbus" in modbus_pkts[0]["proto"]

    capture_text = sniffer.render_capture("pumpehuset", "modbus")
    assert "pumpehuset" in capture_text.lower()
    assert "tshark" in capture_text.lower()
    assert "Modbus" in capture_text

    details = sniffer.render_dissection("pumpehuset", "3")
    assert "Frame 3" in details
    assert "Modbus/TCP" in details

    dcp_capture = sniffer.render_capture("ventil-oen", "dcp")
    assert "PN-DCP" in dcp_capture
    print("  -> Passed.")


def test_hidden_pi_in_ventil_oen():
    print("Test 3: Hidden Pi in Ventil-øen & discovery...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("TestElev", "Automationsteknolog")

    # Navigate to ventil-oen
    engine.handle_command("gå til ventil-oen")
    v_room = ALL_ROOMS["ventil-oen"]
    hotspots_initial = v_room.get_visible_hotspots(engine)
    assert "kabelbakke" in hotspots_initial
    assert "rogue raspberry pi" not in hotspots_initial

    # Inspect cable tray to reveal Pi
    engine.handle_command("undersøg kabelbakke")
    hotspots_after = v_room.get_visible_hotspots(engine)
    assert "rogue raspberry pi" in hotspots_after
    assert "pi-revealed" in engine.flags
    print("  -> Passed.")


def test_pi_forensics_dilemmas():
    print("Test 4: Forensic dilemmas with Rogue Pi...")
    # Test Faraday Bag (Correct)
    fm = ForensicsManager()
    ok, msg = fm.secure_rogue_pi("faraday-pose")
    assert ok is True
    assert fm.pi_handling_state == "secured"
    assert len(fm.evidence_log) == 1
    assert fm.evidence_log[0].sha256 != ""

    # Test Trash (Bad)
    fm2 = ForensicsManager()
    ok2, msg2 = fm2.secure_rogue_pi("smid ud i skraldespand")
    assert ok2 is False
    assert fm2.pi_handling_state == "trashed"
    assert len(fm2.forensic_violations) == 1

    # Test Reuse (Trap)
    fm3 = ForensicsManager()
    ok3, msg3 = fm3.secure_rogue_pi("gem til privat iot genbrug")
    assert ok3 is False
    assert fm3.pi_handling_state == "reused"

    # Test Laptop insertion (Infection)
    fm4 = ForensicsManager()
    ok4, msg4 = fm4.secure_rogue_pi("sd-kort i laptop")
    assert ok4 is False
    assert fm4.pi_handling_state == "infected"
    print("  -> Passed.")


def test_eltavlen_five_paths():
    print("Test 5: El-tavlen 5-way engineering branches (Teach Mode mentor vs Exam Mode consequences)...")
    # Path 1: Correct procedure
    logs1 = []
    e1 = GameEngine(output=logs1.append)
    e1.start("Alice", "Automation")
    e1.handle_command("gå til el-tavlen")
    e1.handle_command("tag offline backup")
    assert "backup-taken" in e1.flags
    e1.handle_command("konfigurer tia portal")
    assert "chapter-3-done" in e1.flags
    assert e1.plc_defect_stop is False

    # In Teach Mode: Hans stops wrong actions before damage occurs and cites NIS2 / IEC 62443
    logs_teach = []
    e_teach = GameEngine(output=logs_teach.append)
    e_teach.start("TeachUser", "Automation")
    e_teach.handle_command("gå til el-tavlen")
    e_teach.handle_command("bloker port 102")
    assert e_teach.plc.f_passivated is False
    assert "HANS GRIBER IND" in "".join(logs_teach)
    assert "NIS2" in "".join(logs_teach)

    # Path 2 (Exam Mode): Hasty Cold Restart (Fails with attack loop)
    logs2 = []
    e2 = GameEngine(output=logs2.append)
    e2.start("Bob", "Automation")
    e2.toggle_game_mode("exam")
    e2.handle_command("gå til el-tavlen")
    e2.handle_command("tving cpu i run")
    assert "KOLDSTART FEJLEDE" in "".join(logs2)
    assert "Det dér havde jeg nok ikke gjort" in "".join(logs2)

    # Path 3 (Exam Mode): Firewall Overkill (Emergency stop & F-I/O passivation)
    logs3 = []
    e3 = GameEngine(output=logs3.append)
    e3.start("Charlie", "Automation")
    e3.toggle_game_mode("exam")
    e3.handle_command("gå til el-tavlen")
    e3.handle_command("bloker port 102")
    assert e3.plc.f_passivated is True
    assert "F-I/O PASSIVERING" in "".join(logs3)

    # Path 4 (Exam Mode): Live Firmware Patch without hash (MitM bootloader lock)
    logs4 = []
    e4 = GameEngine(output=logs4.append)
    e4.start("Dave", "Automation")
    e4.toggle_game_mode("exam")
    e4.handle_command("gå til el-tavlen")
    e4.handle_command("opdater firmware live")
    assert e4.plc.bootloader_locked is True
    assert "BOOTLOADER LÅST" in "".join(logs4)

    # Path 5 (Exam Mode): Unisolated Laptop (ARP spoofing / malware)
    logs5 = []
    e5 = GameEngine(output=logs5.append)
    e5.start("Eve", "Automation")
    e5.toggle_game_mode("exam")
    e5.handle_command("gå til el-tavlen")
    e5.handle_command("kobl laptop i plc port")
    assert "ARP-SPOOFING KAPRET" in "".join(logs5)
    print("  -> Passed.")


def test_kontrolrum_opcua_and_4g():
    print("Test 6: Kontrolrummet OPC UA PKI & 4G backdoor...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Alice", "Automation")
    # Advance to chapter 4
    engine.chapter = 4
    engine.handle_command("gå til kontrolrummet")

    # Disconnect 4G
    engine.handle_command("frakobl 4g-router")
    assert "router-disconnected" in engine.flags

    # Trust client certificate in PKI
    engine.handle_command("godkend scada certifikat")
    assert "cert-trusted" in engine.flags

    # Enforce Basic256Sha256
    engine.handle_command("aktiver opc kryptering")
    assert "opc-crypto-active" in engine.flags

    # Remove Anonymous token
    engine.handle_command("deaktiver anonymous opc")
    assert "anon-disabled" in engine.flags
    assert "chapter-4-done" in engine.flags
    print("  -> Passed.")


def test_dialogues_and_anecdotes():
    print("Test 7: Hans McDonald situational memory, interrogation & Kirsten interim audit (Etape 3)...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Alice", "Automation")
    hans = HansDialogue()

    # Normal state
    g1 = hans.get_greeting(engine)
    assert "pumpe 2 opfører sig" in g1.lower() or "velkommen" in g1.lower()

    # Breaker tripped
    engine.breaker_tripped = True
    g2 = hans.get_greeting(engine)
    assert "k1-sikringen" in g2.lower()

    # Defect stop
    engine.breaker_tripped = False
    engine.plc_defect_stop = True
    g3 = hans.get_greeting(engine)
    assert "defective stop" in g3.lower()

    # Story / anecdote
    anecdote = hans.get_anecdote()
    assert len(anecdote) > 20

    # Interrogation of Hans via terminal command
    logs.clear()
    engine.handle_command("spørg hans om morten")
    m_resp = "\n".join(logs)
    assert "Hydropump Nordic" in m_resp
    assert engine.investigation.get_clue("spor_morten_rapport").discovered is True

    logs.clear()
    engine.handle_command("spørg hans om lars")
    l_resp = "\n".join(logs)
    assert "Lars Kofoed" in l_resp

    logs.clear()
    engine.handle_command("spørg hans om kim")
    k_resp = "\n".join(logs)
    assert "Kim på natholdet" in k_resp

    logs.clear()
    engine.handle_command("spørg hans om modbus")
    assert "Function Code 03" in "\n".join(logs)

    # Kirsten interim audit via phone
    logs.clear()
    engine.handle_command("ring til kirsten")
    interim = "\n".join(logs)
    assert "REVISOR KIRSTEN" in interim
    assert "NIS2 ARTIKEL 23" in interim

    logs.clear()
    engine.handle_command("spørg kirsten om artikel 23")
    assert "24 timer" in "\n".join(logs)

    logs.clear()
    engine.handle_command("spørg kirsten om bøder")
    assert "10 millioner euro" in "\n".join(logs)

    print("  -> Passed.")


def test_incident_reporting_and_audit():
    print("Test 8: NIS2 Incident reporting & Audit report export...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Søren", "Diplomingeniør i IT-Sikkerhed")

    # Early warning report
    engine.handle_command("indberet hændelse")
    assert "early-warning-reported" in engine.flags
    assert engine.incident.early_warning_sent is True

    # Complete objectives to get score
    engine.flags.add("chapter-1-done")
    engine.flags.add("chapter-2-done")
    engine.flags.add("chapter-3-done")
    engine.flags.add("chapter-4-done")
    engine.flags.add("backup-taken")
    engine.flags.add("router-disconnected")
    engine.chapter = 5
    engine.forensics.secure_rogue_pi("faraday-pose")

    # Test audit completion
    engine.handle_command("tal med kirsten")
    assert any("BESTÅET" in l for l in logs)

    # Export report
    engine.handle_command("eksporter rapport")
    assert os.path.exists("NIS2_Audit_Rapport_NordicH2O.md")
    with open("NIS2_Audit_Rapport_NordicH2O.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Søren" in content
    assert "Artikel 21" in content
    assert "Artikel 23" in content
    print("  -> Passed.")


def test_autocomplete_and_number_choices():
    print("Test 9: Autocomplete helper & number input selection...")
    opts = AutocompleteHelper.get_matches("gå")
    assert any("gå til" in o for o in opts)

    # Number input on engine
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Test", "UCL")
    engine.handle_command("gå til pumpehuset")
    # Quick number selection: choice 1 in pumpehuset
    engine.handle_command("1")
    assert len(logs) > 0
    print("  -> Passed.")


def test_teach_vs_exam_modes_and_shuffling():
    print("Test 10: Teach vs Exam modes (no spoilers in choices, Hans stops errors in Teach vs dry comment in Exam)...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Test", "UCL")

    # Verify NO spoiler tags ('Faldgrube', 'Fælde', 'Guldstandard') exist in ANY room in either Teach or Exam mode
    for mode in ("teach", "exam"):
        engine.toggle_game_mode(mode)
        for room_key in ("indgangen", "pumpehuset", "ventil-oen", "el-tavlen", "kontrolrummet"):
            engine.handle_command(f"gå til {room_key}")
            choices = engine.get_current_choices()
            for _k, lbl, _c, _cat in choices:
                assert "Faldgrube" not in lbl, f"Found 'Faldgrube' in {room_key} ({mode}): {lbl}"
                assert "Fælde" not in lbl, f"Found 'Fælde' in {room_key} ({mode}): {lbl}"
                assert "Guldstandard" not in lbl, f"Found 'Guldstandard' in {room_key} ({mode}): {lbl}"

    # Verify choices are renumbered sequentially 1..N
    engine.toggle_game_mode("teach")
    engine.handle_command("gå til pumpehuset")
    pump_teach = engine.get_current_choices()
    keys = [k for k, _l, _c, _cat in pump_teach]
    expected_keys = [str(i) for i in range(1, len(pump_teach) + 1)]
    assert keys == expected_keys

    # Verify in Teach mode: Hans stops hard shutdown before breaker trips
    logs.clear()
    engine.handle_command("hård nødnedlukning af vfd")
    assert engine.breaker_tripped is False
    assert "HANS GRIBER IND" in "\n".join(logs)
    assert "NIS2" in "\n".join(logs)

    # Verify in Exam mode: Hard shutdown executes and trips breaker K1
    engine.toggle_game_mode("exam")
    logs.clear()
    engine.handle_command("hård nødnedlukning af vfd")
    assert engine.breaker_tripped is True
    assert "Det dér havde jeg nok ikke gjort" in "\n".join(logs)

    # Reset breaker for subsequent tests
    engine.reset_safety_breaker()
    engine.toggle_game_mode("teach")
    print("  -> Passed.")


def test_tshark_and_scada_blindness_rule():
    print("Test 11: Real tshark commands, Teach vs Exam SCADA blind failure on missing FC03, and recovery...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Test", "UCL")
    engine.handle_command("gå til pumpehuset")

    # Step 1: Run tshark manual
    logs.clear()
    engine.handle_command("man tshark")
    assert "TSHARK OT QUICK REFERENCE" in "\n".join(logs)

    # Step 2: Run tshark with display filter
    logs.clear()
    engine.handle_command("tshark -Y \"modbus\"")
    combined = "\n".join(logs)
    assert "modbus" in combined.lower()
    assert "FC 03" in combined
    assert "FC 06" in combined

    # Step 3A: In Teach Mode, Hans stops the incomplete firewall rule (--drop-fc 6 without --allow-fc 3)
    logs.clear()
    engine.handle_command("firewall rule add --drop-fc 6")
    assert engine.scada_blind is False
    assert "HANS GRIBER IND" in "\n".join(logs)
    assert "allow-fc 3" in "\n".join(logs)

    # Step 3B: In Exam Mode, forgetting allow FC 03 executes and blinds SCADA
    engine.toggle_game_mode("exam")
    logs.clear()
    engine.handle_command("firewall rule add --drop-fc 6")
    assert engine.scada_blind is True
    assert "scada-blind" in engine.flags
    assert "chapter-1-done" not in engine.flags
    combined_err = "\n".join(logs)
    assert "TAB AF PROCESOVERVÅGNING" in combined_err
    assert "Det dér havde jeg nok ikke gjort" in combined_err

    # Step 4: Verify tshark displays dropped FC 03 telemetry
    logs.clear()
    engine.handle_command("tshark -Y \"modbus\"")
    tshark_output = "\n".join(logs)
    assert "BLOKERET AF FIREWALL - INGEN ALLOW-REGEL FOR FC 03" in tshark_output
    assert "TIMEOUT / CONNECTION RESET" in tshark_output

    # Step 5: Check firewall status
    logs.clear()
    engine.handle_command("firewall status")
    assert "SCADA BLIND! Mangler 'allow-fc 3'" in "\n".join(logs)

    # Step 6: Fix the rule by providing both allow FC 03 and drop FC 06
    logs.clear()
    engine.handle_command("firewall rule add --allow-fc 3 --drop-fc 6")
    assert engine.scada_blind is False
    assert "scada-blind" not in engine.flags
    assert "chapter-1-done" in engine.flags
    assert engine.chapter == 2
    assert "42.0 Bar" in "\n".join(logs)

    # Step 7: Verify tshark now shows successful telemetry
    logs.clear()
    engine.handle_command("tshark -Y \"modbus\"")
    tshark_after = "\n".join(logs)
    assert "DPI ACCEPT: Telemetri OK" in tshark_after
    assert "Stabil drift" in tshark_after
    print("  -> Passed.")


def test_narrative_metrics_and_investigation_board():
    print("Test 12: Narrative 4-metrics system, clues, suspects & case board (Etape 1)...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("TestKonsulent", "Automation & IT")

    # 1. Initial 4 metrics check
    assert engine.metrics.drift == 80
    assert engine.metrics.sikkerhed == 25
    assert engine.metrics.compliance == 40
    assert engine.metrics.tillid == 50

    # 2. Case board initial state
    assert len(engine.investigation.get_discovered_clues()) == 0
    assert len(engine.investigation.suspects) == 5

    # 3. Discovery through physical inspection
    engine.handle_command("gå til pumpehuset")
    logs.clear()
    engine.handle_command("undersøg pumpe 2")
    assert any("NYT SPOR TIL SAGSTAVLEN" in l for l in logs)
    assert engine.investigation.get_clue("spor_manometer_rystelser").discovered is True

    # 4. Discovery through tshark
    logs.clear()
    engine.handle_command("tshark -Y \"modbus\"")
    assert engine.investigation.get_clue("spor_modbus_flood").discovered is True

    # 5. Check suspicion scores updated
    lars = engine.investigation.get_suspect("lars_ex_tekniker")
    assert lars.suspicion_score > 35  # initial was 35, now boosted by clues

    # 6. Test 'sagstavle' command output
    logs.clear()
    engine.handle_command("sagstavle")
    board_output = "\n".join(logs)
    assert "SAGSTAVLE" in board_output
    assert "Drift:" in board_output
    assert "Sikkerhed:" in board_output
    assert "Compliance:" in board_output
    assert "Tillid:" in board_output
    assert "Højhastigheds Modbus" in board_output

    # 7. Test 'spor' and 'analyser spor' commands
    logs.clear()
    engine.handle_command("spor")
    assert "spor_modbus_flood" in "\n".join(logs)

    logs.clear()
    engine.handle_command("analyser spor spor_modbus_flood")
    analysis = "\n".join(logs)
    assert "OT-TEKNISK VURDERING" in analysis
    assert "HYPOTESE-KNYTNING" in analysis

    # 8. Test 'mistænkte' and 'anklag'
    logs.clear()
    engine.handle_command("mistænkte")
    assert "Morten Vestergaard" in "\n".join(logs)
    assert "Lars Kofoed" in "\n".join(logs)

    logs.clear()
    engine.handle_command("anklag lars_ex_tekniker")
    assert "primære arbejdshypotese" in "\n".join(logs)
    assert lars.status == "Hovedmistænkt"

    # 9. Test metric adjustment when solving Chapter 1
    old_drift = engine.metrics.drift
    old_sikkerhed = engine.metrics.sikkerhed
    engine.handle_command("firewall rule add --allow-fc 3 --drop-fc 6")
    assert engine.metrics.drift > old_drift
    assert engine.metrics.sikkerhed > old_sikkerhed

    # 10. Test 'metrikker' command
    logs.clear()
    engine.handle_command("metrikker")
    metr_output = "\n".join(logs)
    assert "HOVEDMETRIKKER" in metr_output
    assert "Drift" in metr_output

    print("  -> Passed.")


def test_investigative_chapter_flow_and_finale():
    print("Test 13: Narrative investigative inquiry across all 5 chapters & Grand Finale (Etape 4)...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Frederik", "Automationsteknolog & IT-Sikkerhed")

    # --- CHAPTER 1: Pumpehuset (Observation -> Data -> Interrogation -> Remediation) ---
    engine.handle_command("gå til pumpehuset")
    p_room = ALL_ROOMS["pumpehuset"]
    desc1 = p_room.get_description(engine)
    assert "Kavitationen er ved at pulverisere pumpehjulet" in desc1

    # Observation
    engine.handle_command("undersøg pumpe 2")
    assert engine.investigation.get_clue("spor_manometer_rystelser").discovered is True

    # Dataindsamling
    engine.handle_command("tshark -Y \"modbus\"")
    assert engine.investigation.get_clue("spor_modbus_flood").discovered is True

    # Afhøring
    engine.handle_command("spørg hans om morten")
    assert engine.investigation.get_clue("spor_morten_rapport").discovered is True

    # Early warning submission
    engine.handle_command("indberet hændelse")

    # Remediation
    engine.handle_command("firewall rule add --allow-fc 3 --drop-fc 6")
    assert engine.chapter == 2
    assert "chapter-1-done" in engine.flags

    # Verify Chapter 1 done description
    desc1_done = p_room.get_description(engine)
    assert "Pumpehuset summer roligt" in desc1_done

    # --- CHAPTER 2: Ventil-øen ---
    engine.handle_command("gå til ventil-oen")
    v_room = ALL_ROOMS["ventil-oen"]
    desc2 = v_room.get_description(engine)
    assert "Festo-ventiler smælder op og i" in desc2

    # Dataindsamling
    engine.handle_command("åbn wireshark")
    assert engine.investigation.get_clue("spor_dcp_storm").discovered is True
    assert engine.investigation.get_clue("spor_mac_oui").discovered is True

    # Fysisk undersøgelse
    engine.handle_command("undersøg kabelbakke")
    assert "pi-revealed" in engine.flags
    assert engine.investigation.get_clue("spor_sort_boks").discovered is True

    # Afhøring
    engine.handle_command("spørg hans om lars")

    # Remediation: Forensisk sikring i Faraday pose
    engine.handle_command("sikr pi i faraday-pose")
    assert "pi-removed" in engine.flags

    # Udskift med SCALANCE switch
    engine.handle_command("udskift switch med scalance")
    assert engine.chapter == 3
    assert "chapter-2-done" in engine.flags

    # --- CHAPTER 3: Hoved-el-tavlen ---
    engine.handle_command("gå til el-tavlen")
    e_room = ALL_ROOMS["el-tavlen"]
    desc3 = e_room.get_description(engine)
    assert "CPU 1516F" in desc3
    assert "STOP-diode" in desc3

    # Observation
    engine.handle_command("undersøg s7-1500")
    assert engine.investigation.get_clue("spor_plc_stop_buffer").discovered is True

    # Undersøg USB
    engine.handle_command("undersøg usb")
    assert engine.investigation.get_clue("spor_usb_backup").discovered is True

    # Remediation: Offline backup + TIA Portal hardening
    engine.handle_command("tag offline backup")
    assert "backup-taken" in engine.flags
    engine.handle_command("konfigurer tia portal")
    assert engine.chapter == 4
    assert "chapter-3-done" in engine.flags

    # --- CHAPTER 4: Kontrolrummet ---
    engine.handle_command("gå til kontrolrummet")
    k_room = ALL_ROOMS["kontrolrummet"]
    desc4 = k_room.get_description(engine)
    assert "4G-router" in desc4
    assert "OPC UA" in desc4

    # Observation
    engine.handle_command("undersøg scada pc")
    assert engine.investigation.get_clue("spor_kim_nattevagt").discovered is True

    # Dataindsamling
    engine.handle_command("undersøg 4g-router")
    assert engine.investigation.get_clue("spor_4g_dongle").discovered is True
    engine.handle_command("åbn wireshark")
    assert engine.investigation.get_clue("spor_opc_leak").discovered is True

    # Afhøring
    engine.handle_command("spørg hans om kim")

    # Remediation
    engine.handle_command("frakobl 4g-router")
    engine.handle_command("godkend scada certifikat")
    engine.handle_command("aktiver opc kryptering")
    engine.handle_command("deaktiver anonymous opc")
    assert engine.chapter == 5
    assert "chapter-4-done" in engine.flags

    # --- CHAPTER 5: Hovedindgangen & Finale ---
    engine.handle_command("gå til indgangen")
    i_room = ALL_ROOMS["indgangen"]
    desc5 = i_room.get_description(engine)
    assert "Tilsynets chefinspektør Kirsten" in desc5

    # 1. Test presentation without prime suspect prompts player
    logs.clear()
    engine.handle_command("fremlæg sagstavle")
    assert "SAGSTAVLE MANGLER HOVEDMISTÆNKT" in "\n".join(logs)

    # 2. Accuse Lars Kofoed
    logs.clear()
    engine.handle_command("anklag lars_ex_tekniker")
    assert "primære arbejdshypotese" in "\n".join(logs)

    # 3. Present case with Lars
    logs.clear()
    engine.handle_command("fremlæg sagstavle")
    case_output = "\n".join(logs)
    assert "DEN STORE KONFRONTATION" in case_output
    assert "Lars Kofoed" in case_output
    assert "Rigspolitiets Nationale Cyber Crime Center (NC3)" in case_output
    assert "case-solved-lars" in engine.flags

    # 4. Carry out final audit with Kirsten and Hans
    logs.clear()
    engine.handle_command("revisor")
    audit_output = "\n".join(logs)
    assert "MILJØ- OG CYBERSIKKERHEDSTILSYNET – AFSLUTTENDE NIS2 AUDIT-DEKRET" in audit_output
    assert "EVALUERING AF ANLÆGGETS 4 HOVEDMETRIKKER" in audit_output
    assert "HANS MCDONALDS DRIFTSDEBRIEFING" in audit_output
    assert "messing-nøglering" in audit_output
    assert "SPILLET ER GENNEMFØRT" in audit_output
    assert engine.running is False

    # 5. Verify exported report contents
    assert os.path.exists("NIS2_Audit_Rapport_NordicH2O.md")
    with open("NIS2_Audit_Rapport_NordicH2O.md", "r", encoding="utf-8") as f:
        report_content = f.read()
    assert "Frederik" in report_content
    assert "Lars Kofoed" in report_content
    assert "Hovedmetrikker for Anlæg og Drift" in report_content
    assert "UCL Faglige Læringsmål" in report_content
    assert "Purdue Modellen & IEC 62443" in report_content

    print("  -> Passed.")


def test_save_and_load_persistence():
    print("Test 14: Save & Load persistence across chapters & metrics...")
    logs = []
    engine1 = GameEngine(output=logs.append)
    engine1.start("SikkerhedsTest", "Automationsteknolog")
    engine1.game_mode = "exam"
    engine1.chapter = 3
    engine1.room = "ventil-oen"
    engine1.flags.add("chapter-1-done")
    engine1.flags.add("chapter-2-done")
    engine1.flags.add("pi-discovered")
    engine1.metrics.adjust_drift(-15, "Test drift drop")
    engine1.metrics.adjust_sikkerhed(25, "Test firewall rule")
    engine1.investigation.prime_suspect_id = "lars_ex_tekniker"
    engine1.investigation.discover_clue("spor_modbus_flood")

    test_save_path = "saves/test_persistence_check.json"
    if os.path.exists(test_save_path):
        os.remove(test_save_path)

    ok, msg = engine1.save_state(test_save_path)
    assert ok is True
    assert os.path.exists(test_save_path)
    assert "gemt" in msg.lower()

    # Load into clean engine2
    engine2 = GameEngine()
    ok_load, load_msg = engine2.load_state(test_save_path)
    assert ok_load is True
    assert "indlæst" in load_msg.lower()

    assert engine2.player.name == "SikkerhedsTest"
    assert engine2.player.education == "Automationsteknolog"
    assert engine2.game_mode == "exam"
    assert engine2.chapter == 3
    assert engine2.room == "ventil-oen"
    assert "chapter-1-done" in engine2.flags
    assert "chapter-2-done" in engine2.flags
    assert "pi-discovered" in engine2.flags
    assert engine2.metrics.drift == engine1.metrics.drift
    assert engine2.metrics.sikkerhed == engine1.metrics.sikkerhed
    assert engine2.investigation.prime_suspect_id == "lars_ex_tekniker"
    assert "spor_modbus_flood" in engine2.investigation.clues
    assert engine2.investigation.clues["spor_modbus_flood"].discovered is True

    # Test list_save_files
    save_list = engine2.list_save_files()
    assert any(s["filename"] == "test_persistence_check.json" for s in save_list)

    # Clean up test save file
    if os.path.exists(test_save_path):
        os.remove(test_save_path)

    print("  -> Passed.")


def test_interactive_tutorial_and_active_clue_analysis():
    print("Test 15: Interactive 5-step Intro-Tutorial (Kapitel 0) & Active Clue Analysis on Sagstavle...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("TutorialElev", "Automationsteknolog", tutorial=True)

    # Verify initial tutorial state (Chapter 0, timers paused, Step 1)
    assert engine.tutorial_active is True
    assert engine.tutorial_step == 1
    assert engine.chapter == 0
    assert engine.timer_started_at == 0.0
    assert engine.elapsed_seconds == 0.0

    # Step 1 -> Step 2: Inspect sign
    engine.handle_command("1")  # Executes 'undersøg skilt'
    assert engine.tutorial_step == 2

    # Step 2 -> Step 3: Run tshark (discovers 'spor_morten_rapport' as unanalyzed)
    engine.handle_command("1")  # Executes 'tshark'
    assert engine.tutorial_step == 3
    morten_clue = engine.investigation.get_clue("spor_morten_rapport")
    assert morten_clue.discovered is True
    assert morten_clue.analyzed is False
    assert len(engine.investigation.get_unanalyzed_clues()) == 1

    # Step 3 -> Step 4: Open Sagstavle
    engine.handle_command("1")  # Executes 'sagstavle'
    assert engine.tutorial_step == 4

    # Step 4A: Analyze the clue (marks analyzed=True and boosts suspicion by +5)
    morten_susp = engine.investigation.get_suspect("morten_pumper")
    score_before_analysis = morten_susp.suspicion_score
    engine.handle_command("analyser spor spor_morten_rapport")
    assert morten_clue.analyzed is True
    assert len(engine.investigation.get_unanalyzed_clues()) == 0
    assert morten_susp.suspicion_score == score_before_analysis + 5
    assert len(engine.investigation.get_analyzed_clues_for_suspect("morten_pumper")) == 1
    # Still in step 4 until a prime suspect is also selected
    assert engine.tutorial_step == 4

    # Step 4B -> Step 5: Select a preliminary prime suspect
    engine.handle_command("anklag morten_pumper")
    assert engine.investigation.prime_suspect_id == "morten_pumper"
    assert engine.tutorial_step == 5

    # Step 5 -> Complete tutorial and enter Chapter 1 (timers start)
    engine.handle_command("1")  # Executes 'afslut tutorial'
    assert engine.tutorial_active is False
    assert engine.tutorial_step == 0
    assert engine.chapter == 1
    assert engine.timer_started_at > 0.0

    # Also test skipping tutorial mid-way
    engine_skip = GameEngine()
    engine_skip.start("SkipElev", "IT-Teknologi", tutorial=True)
    assert engine_skip.tutorial_active is True
    engine_skip.handle_command("spring tutorial over")
    assert engine_skip.tutorial_active is False
    assert engine_skip.chapter == 1
    assert engine_skip.timer_started_at > 0.0

    print("  -> Passed.")


def test_etape2_modular_campaign_variants_and_culprits():
    print("Test 16: Etape 2 Modular Mission Order, 3 Attack Variations (A/B/C) per room & Dynamic Culprits...")
    # Test all 3 variants (A, B, C) and all 4 culprits across different mission orders
    for idx, culprit in enumerate(["lars_ex_tekniker", "morten_pumper", "apt_shadowh2o", "kim_operatoer"]):
        var_choice = ["A", "B", "C"][idx % 3]
        logs = []
        engine = GameEngine(output=logs.append)
        engine.start(f"Agent_{idx}", "Automationsteknolog", randomize=True)
        # Force specific variant & non-standard mission order to test all combinations deterministically
        engine.mission_order = ["el-tavlen", "kontrolrummet", "ventil-oen", "pumpehuset"]
        engine.room_variants = {
            "pumpehuset": var_choice,
            "ventil-oen": var_choice,
            "el-tavlen": var_choice,
            "kontrolrummet": var_choice,
        }
        engine.investigation.configure_dynamic_case(culprit, engine.room_variants)

        # Verify first target room follows mission_order[0] ("el-tavlen")
        assert engine.get_current_target_room() == "el-tavlen"
        engine.handle_command("gå til el-tavlen")
        engine.handle_command("tshark")
        engine.handle_command("undersøg usb")
        engine.handle_command("tag offline backup")
        engine.handle_command("konfigurer tia portal")
        assert "chapter-3-done" in engine.flags
        assert engine.chapter == 2
        assert engine.get_current_target_room() == "kontrolrummet"

        # 2nd room in order: "kontrolrummet"
        engine.handle_command("gå til kontrolrummet")
        engine.handle_command("tshark")
        engine.handle_command("undersøg scada pc")
        engine.handle_command("frakobl 4g-router")
        engine.handle_command("godkend scada certifikat")
        engine.handle_command("aktiver opc kryptering")
        engine.handle_command("deaktiver anonymous opc")
        assert "chapter-4-done" in engine.flags
        assert engine.chapter == 3
        assert engine.get_current_target_room() == "ventil-oen"

        # 3rd room in order: "ventil-oen"
        engine.handle_command("gå til ventil-oen")
        engine.handle_command("tshark")
        engine.handle_command("undersøg kabelbakke")
        engine.handle_command("sikr pi i faraday-pose")
        engine.handle_command("udskift switch med scalance")
        assert "chapter-2-done" in engine.flags
        assert engine.chapter == 4
        assert engine.get_current_target_room() == "pumpehuset"

        # 4th room in order: "pumpehuset"
        engine.handle_command("gå til pumpehuset")
        engine.handle_command("tshark")
        engine.handle_command("spørg hans om morten")
        engine.handle_command("firewall workbench")
        engine.handle_command("monter scalance på din-skinne")
        engine.handle_command("kobl kabler til scalance")
        engine.handle_command("firewall rule add --allow-fc 3 --drop-fc 6")
        assert "chapter-1-done" in engine.flags
        # All 4 rooms solved -> Chapter 5 (Revisor Kirsten at indgangen)
        assert engine.chapter == 5
        assert engine.get_current_target_room() == "indgangen"

        # Analyze all discovered clues and verify true culprit has top suspicion score
        for c in engine.investigation.get_discovered_clues():
            engine.handle_command(f"analyser spor {c.id}")
        top_suspect = max(engine.investigation.suspects.values(), key=lambda s: s.suspicion_score)
        assert top_suspect.id == culprit, f"Expected {culprit} to have highest suspicion, got {top_suspect.id}"

        # Confront at indgangen and complete NIS2 audit
        engine.handle_command("gå til indgangen")
        engine.handle_command("indberet hændelse")
        engine.handle_command(f"anklag {culprit}")
        logs.clear()
        engine.handle_command("fremlæg sagstavle")
        assert "case-solved" in engine.flags
        assert "case-solved-lars" in engine.flags
        engine.handle_command("revisor")
        assert engine.running is False

    print("  -> Passed.")


if __name__ == "__main__":
    test_purdue_and_iec()
    test_sniffer_and_wireshark()
    test_hidden_pi_in_ventil_oen()
    test_pi_forensics_dilemmas()
    test_eltavlen_five_paths()
    test_kontrolrum_opcua_and_4g()
    test_dialogues_and_anecdotes()
    test_incident_reporting_and_audit()
    test_autocomplete_and_number_choices()
    test_teach_vs_exam_modes_and_shuffling()
    test_tshark_and_scada_blindness_rule()
    test_narrative_metrics_and_investigation_board()
    test_investigative_chapter_flow_and_finale()
    test_save_and_load_persistence()
    test_interactive_tutorial_and_active_clue_analysis()
    test_etape2_modular_campaign_variants_and_culprits()
    print("\nALL MECHANICS TESTS PASSED SUCCESSFULLY! [OK]")
