"""Headless GUI test to verify GameApp launches and handles input cleanly."""

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

        # Step 6: Test Mode Toggle (Teach <-> Exam)
        print("  -> Testing Teach vs Exam mode toggle...")
        assert app.engine.game_mode == "teach"
        assert "TEACH" in app.mode_btn.cget("text")
        teach_choices = app.engine.get_current_choices()
        assert any("Faldgrube" in lbl for _k, lbl, _c, _cat in teach_choices)

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

        # Step 8: Test Faldgrube: Byt om på LAN/WAN on workbench
        print("  -> Testing faldgrube on workbench: Byt om på LAN/WAN...")
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

        # Step 10: Test forgetting allow FC 03 (SCADA blind error)
        print("  -> Testing forgetting allow FC 03 on workbench...")
        wb_choices = app.engine.get_current_choices()
        forget_key = [k for k, _l, cmd, _c in wb_choices if "drop-fc 6" in cmd and "allow" not in cmd][0]
        app.command(forget_key)
        app.update()
        assert app.engine.scada_blind is True

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

        app.destroy()
        print("GUI TEST PASSED SUCCESSFULLY! [OK]")
    except tk.TclError as e:
        print(f"Skipping GUI test (No display server available or headless): {e}")

if __name__ == "__main__":
    test_gui()
