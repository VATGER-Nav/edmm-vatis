#!/usr/bin/env python3

import argparse
import json
from datetime import timezone, datetime
import sys
from pathlib import Path

def read_published_serial(path: str) -> int | None:
    try:
        with open(path) as f:
            return json.load(f).get("updateSerial")
    except FileNotFoundError:
        return None


def next_update_serial(current_serial: int | str | None) -> int:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    current = str(current_serial or "")

    if current[:8] == today:
        counter = int(current[8:]) + 1
        if counter > 99:
            raise ValueError(f"updateSerial overflow: already at {current}")
    else:
        counter = 0

    return int(f"{today}{counter:02d}")


def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"error: {path}: invalid JSON: {e}")
    except OSError as e:
        sys.exit(f"error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Releases vATIS profile."
    )
    parser.add_argument("input", type=Path, help="vATIS profile JSON file")
    parser.add_argument("output", type=Path, help="output JSON file")
    args = parser.parse_args()

    profile = load_json(args.input)

    profile["name"] = "EDMM"
    profile["updateUrl"] = "https://raw.githubusercontent.com/VATGER-Nav/edmm-vatis/refs/heads/main/vATIS-EDMM.json"

    profile["updateSerial"] = next_update_serial(read_published_serial(args.output))

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(profile["updateSerial"])


if __name__ == "__main__":
    main()
