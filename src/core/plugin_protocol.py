"""
Unified ModePlugin protocol and plugin discovery mechanism for the microkernel architecture.
"""

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


# [spec: MODE-001]
# [spec: MODE-002]
# [spec: ADMIN-001]
@dataclass
class ModePlugin:
    """Specification contract for a pluggable pedagogical operating mode."""

    key: str
    radio_label: str
    order: int
    requires_framework: bool
    max_history_turns: int
    max_output_tokens: int
    display_name_fn: Callable[[object], str]
    instruction_fn: Callable[[object], str]
    event_card_fn: Callable[[object, str, str, Callable[..., str]], str]


# [spec: MODE-001]
# [spec: MODE-002]
# [spec: ADMIN-001]
def discover_and_register_plugins(
    registry: dict[str, ModePlugin],
    frameworks: dict[str, str],
) -> None:
    """Scan the plugins package and invoke register_plugins(registry, frameworks) on each module."""
    plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
    if not plugins_dir.exists() or not plugins_dir.is_dir():
        return

    for file_path in sorted(plugins_dir.glob("*.py")):
        if file_path.name.startswith("_"):
            continue
        mod_name = f"plugins.{file_path.stem}"
        try:
            mod = importlib.import_module(mod_name)
            register_fn = getattr(mod, "register_plugins", None)
            if callable(register_fn):
                register_fn(registry, frameworks)
        except Exception as err:
            print(f"Notice: unable to load plugin module '{mod_name}': {err}")
