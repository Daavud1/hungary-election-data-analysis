"""Extract supplied 2026 NVI polling-station files into Tableau-ready tables."""

from __future__ import annotations

import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((PROJECT_ROOT / "config" / "source_paths.json").read_text(encoding="utf-8"))
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def clean_name(value: object) -> str:
    """Create stable, readable column names without changing source values."""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def normalized_county(value: object) -> str:
    """Align NVI's county label variants used across supplied workbooks."""
    return str(value).replace(" vármegye", "").replace(" főváros", "").strip()


def read_excel_from_zip(archive: zipfile.ZipFile, name: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(archive.read(name)), sheet_name=sheet_name, header=None)


def data_sheets(archive: zipfile.ZipFile, name: str, excluded: set[str]) -> list[str]:
    return [sheet for sheet in pd.ExcelFile(io.BytesIO(archive.read(name))).sheet_names if sheet not in excluded]


def extract_polling_results(zip_path: str, kind: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a polling-station metrics table and a long vote table for one ballot type."""
    metrics_frames: list[pd.DataFrame] = []
    vote_frames: list[pd.DataFrame] = []
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xls"):
                continue
            for sheet in data_sheets(archive, name, {"Paraméterek"}):
                if sheet.lower().endswith("nemz"):
                    continue
                raw = read_excel_from_zip(archive, name, sheet)
                if len(raw) < 3:
                    continue
                county = normalized_county(raw.iloc[0, 0])
                headers = raw.iloc[1].tolist()
                data = raw.iloc[2:].copy()
                data.columns = [str(value) for value in headers]
                data = data.dropna(how="all")
                data["county"] = county
                data["oevk"] = sheet.split(".")[0].strip() if kind == "individual" else pd.NA
                data["source_file"] = Path(name).name

                first_columns = [column for column in data.columns if not str(column).replace(".0", "").isdigit()]
                metrics = data[first_columns].copy()
                metrics.columns = [clean_name(column) for column in metrics.columns]
                metrics_frames.append(metrics)

                vote_columns = [column for column in data.columns if str(column).replace(".0", "").isdigit()]
                id_columns = [column for column in data.columns if column in first_columns[:2]] + ["county", "oevk", "source_file"]
                long_votes = data[id_columns + vote_columns].melt(
                    id_vars=id_columns,
                    value_vars=vote_columns,
                    var_name="ballot_option_number",
                    value_name="votes",
                )
                long_votes["ballot_option_number"] = long_votes["ballot_option_number"].astype(str).str.replace(".0", "", regex=False)
                long_votes["votes"] = pd.to_numeric(long_votes["votes"], errors="coerce")
                long_votes = long_votes.dropna(subset=["votes"])
                long_votes = long_votes.rename(columns={id_columns[0]: "municipality", id_columns[1]: "polling_station_id"})
                long_votes["county"] = county
                long_votes["oevk"] = sheet.split(".")[0].strip() if kind == "individual" else pd.NA
                vote_frames.append(long_votes)
    return pd.concat(metrics_frames, ignore_index=True), pd.concat(vote_frames, ignore_index=True)


def extract_turnout(path: str) -> pd.DataFrame:
    turnout = pd.read_excel(path)
    turnout.columns = [clean_name(column) for column in turnout.columns]
    turnout["turnout_rate"] = (
        turnout["szavazo_valasztopolgarszam_fo"]
        / turnout["nevjegyzeki_valasztopolgarszam_fo"]
    )
    return turnout


def extract_candidate_lookup(zip_path: str) -> pd.DataFrame:
    """Read candidate number/name mappings from each county archive's parameter sheet."""
    frames: list[pd.DataFrame] = []
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".xls"):
                continue
            parameters = read_excel_from_zip(archive, name, "Paraméterek")
            marker_rows = parameters.index[
                parameters.iloc[:, 0].astype(str).str.contains("Egyéni jelöltek", na=False)
            ].tolist()
            if not marker_rows:
                continue
            start = marker_rows[0] + 2
            lookup = parameters.iloc[start:, :4].copy()
            lookup.columns = ["county", "oevk", "ballot_option_number", "candidate_name"]
            lookup = lookup.dropna(subset=["county", "oevk", "ballot_option_number", "candidate_name"])
            lookup["county"] = lookup["county"].map(normalized_county)
            lookup["oevk"] = lookup["oevk"].astype(str).str.zfill(2)
            lookup["ballot_option_number"] = (
                lookup["ballot_option_number"].astype(str).str.replace(".0", "", regex=False)
            )
            frames.append(lookup)
    return pd.concat(frames, ignore_index=True)


def extract_postal_votes(path: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name="Levélben szavazás jegyzőkönyve", header=None)
    result = raw.iloc[2].copy()
    result.index = raw.iloc[1]
    return pd.DataFrame(
        {
            "election_year": [2026],
            "registered_mail_voters": [result["DL"]],
            "valid_mail_ballots": [result["NL"]],
            "mkkp_votes": [result[1.0]],
            "tisza_votes": [result[2.0]],
            "mi_hazank_votes": [result[3.0]],
            "dk_votes": [result[4.0]],
            "fidesz_kdnp_votes": [result[5.0]],
        }
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    turnout = extract_turnout(SOURCES["turnout_2026"])
    individual_metrics, individual_votes = extract_polling_results(
        SOURCES["individual_polling_results_2026"], "individual"
    )
    list_metrics, list_votes = extract_polling_results(
        SOURCES["list_polling_results_2026"], "list"
    )
    postal_votes = extract_postal_votes(SOURCES["postal_votes_2026"])

    candidate_lookup = extract_candidate_lookup(SOURCES["individual_polling_results_2026"])
    individual_votes = individual_votes.merge(
        candidate_lookup,
        on=["county", "oevk", "ballot_option_number"],
        how="left",
        validate="many_to_one",
    )
    list_party_lookup = pd.DataFrame(
        {
            "ballot_option_number": ["1", "2", "3", "4", "5"],
            "party": ["MKKP", "TISZA", "Mi Hazánk", "DK", "FIDESZ-KDNP"],
        }
    )
    list_votes = list_votes.merge(list_party_lookup, on="ballot_option_number", how="left", validate="many_to_one")

    outputs = {
        "turnout_2026.csv": turnout,
        "individual_polling_metrics_2026.csv": individual_metrics,
        "individual_votes_2026.csv": individual_votes,
        "list_polling_metrics_2026.csv": list_metrics,
        "list_votes_2026.csv": list_votes,
        "postal_votes_2026.csv": postal_votes,
        "candidate_lookup_2026.csv": candidate_lookup,
    }
    for filename, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / filename, index=False, encoding="utf-8-sig")
        print(f"{filename}: {len(frame):,} rows")


if __name__ == "__main__":
    main()
