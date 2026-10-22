"""Create a machine-readable inventory of the locally supplied source files."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    """Return a SHA-256 hash without loading the entire file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_metadata(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader, [])
        rows = sum(1 for _ in reader)
    return {"columns": header, "data_rows": rows}


def zip_metadata(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        names = [entry.filename for entry in entries]
    suffixes = sorted({Path(name).suffix.lower() for name in names if Path(name).suffix})
    return {
        "file_entries": len(entries),
        "sample_entries": names[:15],
        "contained_suffixes": suffixes,
    }


def geojson_metadata(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        features = payload
        geojson_type = "Feature collection stored as a JSON array"
    else:
        features = payload.get("features", [])
        geojson_type = payload.get("type")
    properties = sorted(
        {key for feature in features for key in feature.get("properties", {}).keys()}
    )
    return {
        "geojson_type": geojson_type,
        "feature_count": len(features),
        "property_names": properties,
    }


def file_metadata(label: str, raw_path: str) -> dict[str, Any]:
    path = Path(raw_path)
    result: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        return result

    result.update(
        {
            "kind": "directory" if path.is_dir() else path.suffix.lower().lstrip("."),
            "size_bytes": None if path.is_dir() else path.stat().st_size,
            "sha256": None if path.is_dir() else sha256(path),
        }
    )
    if path.is_dir():
        zips = sorted(path.glob("*.zip"))
        result["zip_files"] = len(zips)
        result["sample_files"] = [file.name for file in zips[:15]]
    elif path.suffix.lower() == ".csv":
        result.update(csv_metadata(path))
    elif path.suffix.lower() == ".zip":
        result.update(zip_metadata(path))
    elif path.suffix.lower() in {".geojson", ".json"}:
        result.update(geojson_metadata(path))
    return result


def build_inventory(config_path: Path) -> list[dict[str, Any]]:
    sources = json.loads(config_path.read_text(encoding="utf-8"))
    return [file_metadata(label, path) for label, path in sources.items()]


def main() -> None:
    config_path = PROJECT_ROOT / "config" / "source_paths.json"
    output_path = PROJECT_ROOT / "data" / "interim" / "source_inventory.json"
    inventory = build_inventory(config_path)
    output_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(inventory)} source records to {output_path}")
    for source in inventory:
        print(f"- {source['label']}: {'found' if source['exists'] else 'missing'}")


if __name__ == "__main__":
    main()
