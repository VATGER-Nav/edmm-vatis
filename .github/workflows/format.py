#!/usr/bin/env python3

import argparse
import copy
import json
import sys
from pathlib import Path


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


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
        description="Standardize station atisFormat entries in a vATIS profile."
    )
    parser.add_argument("input", type=Path, help="vATIS profile JSON file")
    parser.add_argument("output", type=Path, help="output JSON file")
    args = parser.parse_args()

    atis_format_dir = args.input.resolve().parent / "atis-format"
    base_path = atis_format_dir / "base.json"
    if not base_path.is_file():
        sys.exit(f"error: base format file not found: {base_path}")

    base = load_json(base_path)
    profile = load_json(args.input)

    stations = profile.get("stations")
    if not isinstance(stations, list):
        sys.exit(f"error: {args.input}: no 'stations' list found")

    for station in stations:
        identifier = station.get("identifier", "<unknown>")
        override_path = atis_format_dir / f"override-{identifier}.json"
        if override_path.is_file():
            station["atisFormat"] = deep_merge(base, load_json(override_path))
            print(f"{identifier}: base + {override_path.name}")
        else:
            station["atisFormat"] = copy.deepcopy(base)
            print(f"{identifier}: base")

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
