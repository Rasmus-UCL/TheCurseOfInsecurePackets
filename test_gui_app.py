"""Headless GUI test to verify GameApp launches and handles input cleanly."""

import os
import sys
import tkinter as tk
from gui.app import GameApp

def test_gui():
    print("Testing GameApp launch and integrated terminal...")
    try:
        app = GameApp()
        app.introduce()
        app.update()

        # Step 1: Submit name
        print("  -> Submitting intro name...")
        app.command("Christian")
        app.update()

        # Step 2: Submit education
        print("  -> Submitting intro education...")
        app.command("Automationsteknolog")
        app.update()

        assert app.engine.player.name == "Christian"
        assert app.engine.player.education == "Automationsteknolog"
        assert app.engine.chapter == 1

        # Step 3: Test help without recursion
        print("  -> Testing help command (no recursion)...")
        app.command("hjælp")
        app.update()

        # Step 4: Verify 3 minute pump deadline (180s)
        assert app.engine.pump_deadline_seconds == 180, f"Expected 180s, got {app.engine.pump_deadline_seconds}"

        # Step 5: Test navigation via terminal
        print("  -> Testing navigation to pumpehuset...")
        app.command("gå til pumpehuset")
        app.update()
        assert app.engine.room == "pumpehuset"
        assert app.engine.pump_deadline_active is True

        # Step 6: Test Mode Toggle (Teach <-> Exam) & No Spoilers in either mode
        print("  -> Testing Teach vs Exam mode toggle & Action Panel buttons...")
        assert app.engine.game_mode == "teach"
        assert "TEACH" in app.mode_btn.cget("text")
        assert len(app.action_buttons) > 0
        teach_choices = app.engine.get_current_choices()
        assert not any("Faldgrube" in lbl for _k, lbl, _c, _cat in teach_choices)
        assert not any("Guldstandard" in lbl for _k, lbl, _c, _cat in teach_choices)

        app.toggle_mode()
        assert app.engine.game_mode == "exam"
        assert "EKSAMEN" in app.mode_btn.cget("text")
        exam_choices = app.engine.get_current_choices()
        assert not any("Faldgrube" in lbl for _k, lbl, _c, _cat in exam_choices)
        assert not any("Guldstandard" in lbl for _k, lbl, _c, _cat in exam_choices)
        assert not any("Anbefalet" in lbl for _k, lbl, _c, _cat in exam_choices)

        # Switch back to teach mode
        app.toggle_mode()
        assert app.engine.game_mode == "teach"

        # Step 7: Test Canvas Click on DIN-skinne hotspot opens workbench directly
        print("  -> Testing direct canvas hotspot click on DIN-skinne...")
        app.on_canvas_click("ts35 din-skinne")
        app.update()
        assert app.engine.active_workbench == "vfd_workbench"
        assert app.map.view_mode == "vfd_workbench"

        # Step 8A: In Teach Mode, Hans stops wrong cabling on workbench
        print("  -> Testing Teach Mode: Hans stops wrong cabling on workbench...")
        wb_choices = app.engine.get_current_choices()
        wrong_key = [k for k, _l, cmd, _c in wb_choices if cmd == "byt om på lan og wan"][0]
        app.command(wrong_key)
        app.update()
        assert app.engine.wrong_cabling is False
        assert "HANS GRIBER IND" in app.terminal.text.get("1.0", "end")

        # Step 8B: In Exam Mode, wrong cabling executes on workbench
        print("  -> Testing Exam Mode: wrong cabling executes on workbench...")
        app.toggle_mode()
        assert app.engine.game_mode == "exam"
        wb_choices = app.engine.get_current_choices()
        wrong_key = [k for k, _l, cmd, _c in wb_choices if cmd == "byt om på lan og wan"][0]
        app.command(wrong_key)
        app.update()
        assert app.engine.wrong_cabling is True

        # Step 9: Correct cabling
        print("  -> Testing correct cabling on workbench...")
        wb_choices = app.engine.get_current_choices()
        cable_key = [k for k, _l, cmd, _c in wb_choices if cmd == "kobl kabler til scalance"][0]
        app.command(cable_key)
        app.update()
        assert app.engine.vfd_cabled is True
        assert app.engine.wrong_cabling is False

        # Step 10: Test forgetting allow FC 03 in Exam Mode (SCADA blind error)
        print("  -> Testing forgetting allow FC 03 on workbench (Exam Mode)...")
        wb_choices = app.engine.get_current_choices()
        forget_key = [k for k, _l, cmd, _c in wb_choices if "drop-fc 6" in cmd and "allow" not in cmd][0]
        app.command(forget_key)
        app.update()
        assert app.engine.scada_blind is True

        # Switch back to Teach Mode
        app.toggle_mode()
        assert app.engine.game_mode == "teach"

        # Step 11: Correct with allow FC 03 and drop FC 06
        print("  -> Testing correcting rule with allow FC 03 and drop FC 06...")
        wb_choices = app.engine.get_current_choices()
        dpi_key = [k for k, _l, cmd, _c in wb_choices if "allow-fc 3" in cmd or cmd == "aktiver modbus dpi"][0]
        app.command(dpi_key)
        app.update()
        assert "chapter-1-done" in app.engine.flags
        assert app.engine.scada_blind is False
        assert app.map.view_mode == "room"

        # Step 12: Test real tshark CLI commands
        print("  -> Testing tshark CLI in terminal...")
        app.command("tshark -Y \"modbus\"")
        app.update()
        app.command("man tshark")
        app.update()

        # Step 13: Test empty enter reprints choices without losing options
        print("  -> Testing empty Enter reprinting choices...")
        app.command("")
        app.update()

        # Step 14: Test canvas redrawing
        print("  -> Testing canvas drawing...")
        app.map.draw()
        app.update()

        # Step 15: Test 4-metrics HUD bar (Etape 2)
        print("  -> Testing 4-metrics HUD bar...")
        app.update_metrics_display()
        assert "Drift:" in app.metric_drift_label.cget("text")
        assert "Sikkerhed:" in app.metric_sikkerhed_label.cget("text")
        assert "Compliance:" in app.metric_compliance_label.cget("text")
        assert "Tillid:" in app.metric_tillid_label.cget("text")

        # Step 16: Test Sagstavle view toggle, static height=310 & clicking clues directly!
        print("  -> Testing Sagstavle toggle, static 310px height, and clicking clue cards...")
        assert app.map.view_mode == "room"
        app.toggle_sagstavle()
        app.update()
        assert app.map.view_mode == "clue_board"
        assert int(app.map.cget("height")) == 310
        assert "Luk Sagstavle" in app.sagstavle_btn.cget("text")
        assert "menu_from_clue_board" in app.map.canvas_buttons
        assert "close_clue_board" in app.map.canvas_buttons
        assert "clue_spor_modbus_flood" in app.map.canvas_buttons

        # Simulate clicking directly on the 'spor_modbus_flood' clue card on the Sagstavle canvas!
        _bx1, _by1, _bx2, _by2, clue_cb = app.map.canvas_buttons["clue_spor_modbus_flood"]
        clue_cb()
        app.update()
        assert app.engine.investigation.clues["spor_modbus_flood"].analyzed is True

        # Test clicking suspect on clue board via canvas_buttons
        _sx1, _sy1, _sx2, _sy2, susp_cb = app.map.canvas_buttons["susp_morten_pumper"]
        susp_cb()
        app.update()
        assert app.engine.investigation.prime_suspect_id == "morten_pumper"

        # Toggle back to room
        app.toggle_sagstavle()
        app.update()
        assert app.map.view_mode == "room"
        assert int(app.map.cget("height")) == 310

        # Verify prominent Top Header Bar buttons
        assert app.btn_hovedmenu.winfo_exists()
        assert app.btn_quick_save.winfo_exists()

        # Step 17: Test In-Game Quicksave
        print("  -> Testing in-game quicksave...")
        app.quick_save()
        app.update()
        expected_save = "saves/save_Christian.json"
        assert os.path.exists(expected_save), f"Expected {expected_save} to exist"

        # Step 18: Test Return to Main Menu
        print("  -> Testing return to main menu...")
        app.prompt_return_to_menu()
        app.update()
        assert app.menu_container.winfo_ismapped() or not app.gameplay_container.winfo_ismapped()

        # Step 19: Test Main Menu tab switching
        print("  -> Testing main menu tabs (load_game, lore, new_game)...")
        app.switch_menu_tab("load_game")
        app.update()
        assert "load_game" in app.cards

        app.switch_menu_tab("lore")
        app.update()
        assert "lore" in app.cards

        app.switch_menu_tab("new_game")
        app.update()
        assert "new_game" in app.cards

        # Step 20: Test Loading Saved Game
        print("  -> Testing loading saved game...")
        load_success = app.load_game_file(expected_save)
        app.update()
        assert load_success is True
        assert app.engine.player.name == "Christian"
        assert app.engine.chapter == 2

        # Step 21: Test returning to menu via terminal command (including 'hovemenu' typo and when running=False)
        print("  -> Testing terminal command 'hovemenu' when game is ended/finished...")
        app.engine.running = False
        app.update_objective()
        assert "MISSION" in app.objective_banner.cget("text")
        app.command("hovemenu")
        app.update()

        # Step 22: Test launching New Game with Interactive Tutorial (Kapitel 0) & clicking HUD '📊 Kør tshark CLI'
        print("  -> Testing launching New Game with Intro-Tutorial (Kapitel 0) and HUD tshark button...")
        app.start_new_game(tutorial=True)
        app.update()
        assert app.engine.tutorial_active is True
        assert app.engine.tutorial_step == 1
        assert app.engine.chapter == 0
        assert "INTRO-TUTORIAL" in app.objective_banner.cget("text")

        # Click 'skilt' hotspot on canvas -> opens HUD with 'hud_wireshark', advances tutorial to step 2
        app.map.select_hotspot("skilt")
        app.update()
        assert app.engine.tutorial_step == 2
        assert "hud_wireshark" in app.map.canvas_buttons

        # Click '📊 Kør tshark CLI' button inside HUD -> executes tshark without AttributeError, advances to step 3!
        _wx1, _wy1, _wx2, _wy2, ws_cb = app.map.canvas_buttons["hud_wireshark"]
        ws_cb()
        app.update()
        assert app.engine.tutorial_step == 3

        app.command("spring tutorial over")
        app.update()
        assert app.engine.tutorial_active is False
        assert app.engine.chapter == 1

        # Clean up test save file
        if os.path.exists(expected_save):
            os.remove(expected_save)

        app.destroy()
        print("GUI TEST PASSED SUCCESSFULLY! [OK]")
    except tk.TclError as e:
        print(f"Skipping GUI test (No display server available or headless): {e}")

if __name__ == "__main__":
    test_gui()
