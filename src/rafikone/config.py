from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "rafikone"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ConfigError(Exception):
    pass


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise ConfigError(
            "Configuration not found. Run 'rafikone init' to set up the project root."
        )
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data: dict) -> None:
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_project_root() -> Path:
    cfg = load_config()
    root = cfg.get("project_root")
    if not root:
        raise ConfigError("project_root not set in config. Run 'rafikone init'.")
    path = Path(root).expanduser().resolve()
    if not path.exists():
        raise ConfigError(f"Project root does not exist: {path}")
    return path


def set_project_root(path: str) -> None:
    resolved = Path(path).expanduser().resolve()
    save_config({"project_root": str(resolved)})


def get_config() -> dict:
    return load_config()
