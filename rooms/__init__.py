"""Rooms and physical zones package for The Curse of Insecure Packets."""

from rooms.base import BaseRoom
from rooms.indgangen import IndgangenRoom
from rooms.pumpehuset import PumpehusetRoom
from rooms.ventil_oen import VentilOenRoom
from rooms.el_tavlen import ElTavlenRoom
from rooms.kontrolrummet import KontrolrummetRoom

ALL_ROOMS: dict[str, BaseRoom] = {
    "indgangen": IndgangenRoom(),
    "pumpehuset": PumpehusetRoom(),
    "ventil-oen": VentilOenRoom(),
    "el-tavlen": ElTavlenRoom(),
    "kontrolrummet": KontrolrummetRoom(),
}

__all__ = [
    "BaseRoom",
    "IndgangenRoom",
    "PumpehusetRoom",
    "VentilOenRoom",
    "ElTavlenRoom",
    "KontrolrummetRoom",
    "ALL_ROOMS",
]
