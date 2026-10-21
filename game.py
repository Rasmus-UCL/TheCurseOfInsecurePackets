"""Main entry point for The Curse of Insecure Packets.

The graphical client is the default. Use ``--cli`` for the terminal version.
"""

from __future__ import annotations

import sys

from engine import GameEngine


def run_cli() -> None:
    """Start the optional text client."""
    print("THE CURSE OF INSECURE PACKETS")
    name = input("Hvad hedder du? ").strip()
    education = input("Hvilken uddannelse kommer du fra? ").strip()
    game = GameEngine()
    game.start(name, education)
    print("Skriv HJÆLP for kommandoer.")
    while game.running:
        try:
            game.handle_command(input("\n> "))
        except (EOFError, KeyboardInterrupt):
            print()
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
