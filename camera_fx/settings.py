"""Effect catalog and local preferences; never stores camera images."""
import json
from pathlib import Path

CATALOG = {
    "teleport": ("Goku · Teletransporte", "Dos dedos junto a la frente", "2"),
    "clones": ("Naruto · Kage Bunshin", "Dos manos con indices juntos", "3"),
    "rasengan": ("Naruto · Rasengan", "Palma abierta hacia la camara", "4"),
    "aura": ("Super Saiyan · Aura dorada", "Puno cerrado (cuatro dedos doblados)", "5"),
    "matrix": ("Matrix · Lluvia digital", "Cuernos: indice y menique extendidos", "6"),
}
DEFAULT_ENABLED = {"teleport"}
SETTINGS_PATH = Path(__file__).resolve().parents[1] / "app-settings.json"


def load_enabled(path=SETTINGS_PATH):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        enabled = data["enabled_effects"]
        if not isinstance(enabled, list) or not all(isinstance(x, str) for x in enabled):
            raise ValueError("Invalid preferences")
        return set(enabled) & CATALOG.keys()
    except (OSError, ValueError, KeyError, TypeError):
        return DEFAULT_ENABLED.copy()


def save_enabled(enabled, path=SETTINGS_PATH):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"enabled_effects": sorted(set(enabled) & CATALOG.keys())}, indent=2), encoding="utf-8")
    temporary.replace(path)
