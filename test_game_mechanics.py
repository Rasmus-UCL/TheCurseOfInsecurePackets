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
    print("Test 5: El-tavlen 5-way engineering branches...")
    # Path 1: Golden Standard
    logs1 = []
    e1 = GameEngine(output=logs1.append)
    e1.start("Alice", "Automation")
    e1.handle_command("gå til el-tavlen")
    e1.handle_command("tag offline backup")
    assert "backup-taken" in e1.flags
    e1.handle_command("konfigurer tia portal")
    assert "chapter-3-done" in e1.flags
    assert e1.plc_defect_stop is False

    # Path 2: Hasty Cold Restart (Fails with attack loop)
    logs2 = []
    e2 = GameEngine(output=logs2.append)
    e2.start("Bob", "Automation")
    e2.handle_command("gå til el-tavlen")
    e2.handle_command("tving cpu i run")
    assert "KOLDSTART FEJLEDE" in "".join(logs2)

    # Path 3: Firewall Overkill (Emergency stop & F-I/O passivation)
    logs3 = []
    e3 = GameEngine(output=logs3.append)
    e3.start("Charlie", "Automation")
    e3.handle_command("gå til el-tavlen")
    e3.handle_command("bloker port 102")
    assert e3.plc.f_passivated is True
    assert "F-I/O PASSIVERING" in "".join(logs3)

    # Path 4: Live Firmware Patch without hash (MitM bootloader lock)
    logs4 = []
    e4 = GameEngine(output=logs4.append)
    e4.start("Dave", "Automation")
    e4.handle_command("gå til el-tavlen")
    e4.handle_command("opdater firmware live")
    assert e4.plc.bootloader_locked is True
    assert "BOOTLOADER LÅST" in "".join(logs4)

    # Path 5: Unisolated Laptop (ARP spoofing / malware)
    logs5 = []
    e5 = GameEngine(output=logs5.append)
    e5.start("Eve", "Automation")
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
    print("Test 10: Teach vs Exam modes, shuffling, and auto-reprinting...")
    logs = []
    engine = GameEngine(output=logs.append)
    engine.start("Test", "UCL")

    # In Indgangen: Teach mode
    assert engine.game_mode == "teach"
    t_choices = engine.get_current_choices()
    assert any("Start indsats" in lbl for _k, lbl, _c, _cat in t_choices)

    # Toggle to Exam mode
    engine.toggle_game_mode("exam")
    assert engine.game_mode == "exam"
    e_choices = engine.get_current_choices()
    assert not any("Start indsats" in lbl for _k, lbl, _c, _cat in e_choices)

    # Pumpehuset exam mode: no Faldgrube spoilers
    engine.handle_command("gå til pumpehuset")
    pump_exam = engine.get_current_choices()
    assert not any("Faldgrube" in lbl for _k, lbl, _c, _cat in pump_exam)
    assert not any("Guldstandard" in lbl for _k, lbl, _c, _cat in pump_exam)

    # Switch back to teach mode in Pumpehuset
    engine.toggle_game_mode("teach")
    pump_teach = engine.get_current_choices()
    assert any("Faldgrube" in lbl for _k, lbl, _c, _cat in pump_teach)

    # Verify choices are renumbered sequentially 1..N
    keys = [k for k, _l, _c, _cat in pump_teach]
    expected_keys = [str(i) for i in range(1, len(pump_teach) + 1)]
    assert keys == expected_keys

    # Verify auto-reprint after command: menu is printed at end of output
    logs.clear()
    engine.handle_command("undersøg pumpe 2")
    combined_log = "\n".join(logs)
    assert "TILGÆNGELIGE VALG [🎓 TEACH MODE" in combined_log

    print("  -> Passed.")


def test_tshark_and_scada_blindness_rule():
    print("Test 11: Real tshark commands, SCADA blind failure on missing FC03, and recovery...")
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

    # Step 3: Critical mistake: Forget allow FC 03 (only drop FC 06)
    logs.clear()
    engine.handle_command("firewall rule add --drop-fc 6")
    assert engine.scada_blind is True
    assert "scada-blind" in engine.flags
    assert "chapter-1-done" not in engine.flags
    combined_err = "\n".join(logs)
    assert "SCADA-ALARM" in combined_err
    assert "GLEMTE at tillade WinCC SCADA's FC 03" in combined_err

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
    print("\nALL MECHANICS TESTS PASSED SUCCESSFULLY! [OK]")
